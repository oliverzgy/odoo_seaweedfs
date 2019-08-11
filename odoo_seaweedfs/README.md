使用此模块需要配置相应的文件/图片服务器，步骤 - 

服务器环境：Ubuntu 16.04, docker, docker-compose

### 配置文件服务器

1. 下载 https://github.com/chrislusf/seaweedfs
2. cd seaweedfs/docker
3. sudo docker-compose up -d

生产环境配置，可以参考： https://github.com/chrislusf/seaweedfs/wiki

### 设置反向代理

4. 设置反向代理仅仅允许get请求，域名: images.yourdomain.com，参考：https://stackoverflow.com/questions/42512725/limiting-http-request-in-nginx
5. 设置反向代理允许全部操作（有安全验证），域名 console.images.yourdomain.com

### 模块设置

 1. 安装基础文件模块
 2. 设置文件服务器配置信息，路径：存储/配置/设置
