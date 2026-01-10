import axios from 'axios';

// 假设后端运行在 localhost:8000
const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// 请求拦截器：添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token 过期或无效，清除 token 并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  formData.append('grant_type', 'password'); // OAuth2 规范

  // 根据后端接口定义发送数据，后端 schemas.UserLogin 接收 user_credentials: schemas.UserLogin
  // 但是后端 main.py 里 @app.post("/auth/login") 接收 user_credentials: schemas.UserLogin
  // schemas.UserLogin 是 json body, 包含 username, password
  // 不过通常 oauth2_scheme 是表单形式。
  // 让我们再检查下 backend/main.py 的 login 实现
  /*
  @app.post("/auth/login", response_model=schemas.Token)
  def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
       user = auth.authenticate_user(db, user_credentials.username, user_credentials.password)
  */
  // 它接收的是 JSON body 的 UserLogin 对象，而不是标准的 OAuth2 表单数据
  
  const response = await api.post('/auth/login', { username, password });
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
    // 保存用户信息，如果有的话
    if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
    }
  }
  return response.data;
};

export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
};

export default api;
