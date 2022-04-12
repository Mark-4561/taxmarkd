# 写在最前面：强烈建议先阅读官方教程[Dockerfile最佳实践]（https://docs.docker.com/develop/develop-images/dockerfile_best-practices/）
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能提及小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。
# 选择基础镜像
FROM alpine:3.13

# 容器默认时区为UTC，如需使用上海时间请启用以下时区设置命令
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 选用国内镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories 
RUN apk add --update --no-cache curl jq py3-configobj py3-pip py3-setuptools python3 python3-dev \

&& apk add bash \
&& apk add build-base \
&& apk add jpeg-dev zlib-dev \
&& apk add freetds-dev \
&& apk add ca-certificates \
&& apk add wget \
&& apk add iputils \
&& apk add iproute2 \
&& apk add libc6-compat \
&& apk add -U tzdata \

&& rm -rf /var/cache/apk/* 

# 拷贝当前项目到/app目录下
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
# pip install scipy 等数学包失败，可使用 apk add py3-scipy 进行， 参考安装 https://pkgs.alpinelinux.org/packages?name=py3-scipy&branch=v3.1
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple
RUN pip config set global.trusted-host mirrors.cloud.tencent.com/pypi/simple
RUN pip install --upgrade pip
RUN pip install -U wheel
RUN pip install install -U cos-python-sdk-v5 
RUN pip install torchvision >= 0.9.0
RUN pip install torch >= 1.8.0
RUN pip install --user -r requirements.txt

# 设定对外端口
EXPOSE 80

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]


# python3 py3-pip 