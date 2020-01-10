一个网页版的串口工具

与一个本地串口工具一样，不过是在网页端，可以在远程打开

后端使用flask框架，使用python serial模块

通信使用websocket


目前还在开发中


界面比较丑陋，基本功能实现了

![主界面](./static/demo.jpg)

使用方法：

下载代码，安装依赖: `pip3 install flask socketio pyserial`

直接运行: `python3 run.py` 就可以了 默认端口号5000

这样你就可以在本地浏览器使用远端的串口比如树莓派



### License
Apache Dubbo is under the Apache 2.0 license. See the LICENSE file for details.
