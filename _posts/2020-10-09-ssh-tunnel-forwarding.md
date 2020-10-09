---
layout: post
title: SSH Port Forwarding笔记
tags:
  - ssh port forwarding
  - ssh tunnel
comments: true
published: true
---

## SSH端口转发 和 SSH隧道
SSH 端口转发（SSH Port Forwarding）是一种 通过搭建一条 SSH隧道（SSH tunnel）连接客户端（client）和服务器(server)的技术。
它通常用于外网的计算机访问内网的服务，或者将内网的服务暴露到外网。 根据这两种不同的用法，SSH 端口转发主要分为2种:

## Local Forwarding

local forwarding 通常用于外网计算机访问内网服务， 它的原理 是 在本机(localhost)和 远端主机（remotehost/gatehost）之间搭建一条ssh 隧道， 然后将来自本地特定端口，这里称为sourcePort，的请求 通过ssh隧道发送给远端主机(remotehost)或者远端主机所能连接到的内网的主机（farawayhost）的特定端口，这里称为onPort。

<img src="/img/2020-10-09-ssh-tunnel-forwarding/localforward.png" alt="drawing" width="800"/>


### 具体命令
```bash
ssh -L sourcePort:farawayhost:onPort remotehost
```
这条命令的意思是: 使用 ssh 将本主机(localhost)连接到remotehost, 然后将所有访问本地的sourcePort的请求转发到一个叫farawayhost的onPort端口上去，而这个farawayhost，remotehost能访问到（本主机访问不到）。

### 具体例子
Example 1:
```bash
ssh -L 80:localhost:80 SUPERSERVER
```
当前主机（localhost）的80端口被转发到SUPERSERVER的80端口上。当某人A打开浏览器访问本机时，A将收到SUPERSERVER的服务的返回结果。而实际上，localhost可以没有运行在80端口的服务。

Example 2:
```bash
ssh -L 5432:internalpostgres.com:5432 gateserver
```
当前主机（localhost）的5432端口被转发到通过网关(gateserver)可以访问的内部的postgres数据库服务器（internalpostgres.com）的5432端口上。 这样A就可以通过访问localhost的5432端口来查询内部数据服务器中的数据了。


Local forwarding 通常被用来`穿透`（penetrate）内网，访问内网服务，从当前主机（localhost）来看，整个过程是一个推（push）的动作。

## Remote Forwarding
remote forwarding 通常用于将本机能访问的内网的服务（或者说端口）暴露给外网。它的原理是 在本机(localhost)和 远端主机（remotehost/gatehost）之间搭建一条ssh 隧道，然后将来自远端主机特定端口， 这里称为sourcePort，的请求通过ssh隧道发送给本机（localhost）或者本机所能连接到的内部主机（nearhost）的特定端口，这里称为onPort。

<img src="/img/2020-10-09-ssh-tunnel-forwarding/remoteforward.png" alt="drawing" width="800"/>

### 具体命令
```bash
ssh -R sourcePort:nearhost:onPort remotehost
```
使用 ssh 将本主机(localhost)连接到remotehost, 然后将所有访问remotehost的sourcePort的请求转发到一个叫nearhost的onPort端口上去，而这个nearhost，本主机(localhost)能访问到（当前主机局域网外部的网络访问不到）。

### 具体例子
Example 3:
```bash
ssh -R 80:localhost:80 tinyserver
```
访问tinyserver的80端口的请求，都将被转发到本机，如果本机上运行这web服务，那么访问tinyserver 80端口的请求将收到本机的回复

Example 4:
```bash
ssh -R 80:SUPERSERVER:30180 tinyserver1
ssh -R 80:SUPERSERVER:30280 tinyserver2
```
访问tinyserver1， tinyserver2 80端口的请求，都将通过本机，被转发到本机能访问的SUPERSERVER的30180，30280端口上去。

Remote forwarding 通常被用于将内网的服务`赋能`于外网的机器，前提是它需要有独立的ip。 从当前主机（localhost）来看，整个过程是一个拉（pull）的动作。

## 其他的一些
1. Local forwarding 和 Remote forwarding 在localhost 和remotehost 都有独立ip时，可以替换使用。 但是通常情况下，只有它们中只有一个有独立ip，那么有独立ip的被用作remotehost， 然后根据需要选在使用local forwarding 还是remote forwarding
2. 还有一个Dynamic forwarding 的端口转发， 它和local forwarding 类似，但是于local forwarding 将请求转发到farawayhost特定端口上不同，它只是将localhost 所连接的remotehost变成了localhost的一个socks5代理，代理上可以运行多种协议，例如浏览器可以socks代理处理HTTP HTTPS FTP协议。
```bash
ssh -D 9090 remotehost 
```
这条命令的意思是remotehost 将被作为本地（localhost）的一个socks代理，端口是9090。 所有访问本地9090的请求将被发送到remote后，在流向互联网。

## 引用
[What's ssh port forwarding and what's the difference between ssh local and remote port forwarding](https://unix.stackexchange.com/questions/115897/whats-ssh-port-forwarding-and-whats-the-difference-between-ssh-local-and-remot)

[SSH Port Forwarding Example](https://www.ssh.com/ssh/tunneling/example)

[SSH Port Forwarding](https://zaiste.net/posts/ssh-port-forwarding/)