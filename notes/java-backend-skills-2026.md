# Java 后端工程师核心技能栈（2026版）

> 来源：11条完整技能要求整理  
> 核心观点：后端基本盘，不管AI怎么发展都要会

---

## 01. 语言基础

| 要求 | 说明 |
|------|------|
| Java 8~26 | 掌握新特性 |
| 集合框架 | `List`、`Set`、`Map` 源码、`Stream API` |
| 反射 & 动态代理 | AOP、Spring 核心机制 |
| 异常处理 | 自定义异常、全局异常处理 |

**面试重点**：HashMap 源码（拉链法、红黑树）、ConcurrentHashMap（分段锁→CAS）

---

## 02. 主流框架

| 框架 | 要求 |
|------|------|
| Spring Boot 3 | IOC、AOP、自动配置原理 |
| MyBatis-Plus | 代码生成器、分页插件、Lambda 查询 |
| Spring Cloud | 微服务组件（Nacos/Consul、Gateway、Feign、Sentinel、Seata） |
| 分布式事务 | Seata AT 模式、TCC 模式、Saga 模式 |

**简历亮点**：熟悉 Spring 生命周期 → 被追问也能对答如流

---

## 03. 数据库

| 要求 | 说明 |
|------|------|
| MySQL | 表设计、索引设计、事务隔离级别 |
| SQL 调优 | Explain 分析、慢查询优化 |
| 分库分表 | ShardingSphere、水平/垂直拆分 |
| 索引优化 | 最左前缀、覆盖索引、回表优化 |

---

## 04. 缓存

| 组件 | 要求 |
|------|------|
| Redis | String、Hash、ZSet、Pub/Sub、Lua 脚本 |
| Caffeine | 本地缓存、多级缓存 |
| 分布式锁 | Redisson、锁续期、可重入 |
| 缓存问题 | 穿透、击穿、雪崩解决方案 |

---

## 05. 部署运维

| 工具 | 用途 |
|------|------|
| Docker | 容器化打包、Docker Compose |
| Nginx | 反向代理、负载均衡、SSL 配置 |
| Serverless | 阿里云函数计算、弹性伸缩 |

---

## 06. 监控告警

| 工具 | 用途 |
|------|------|
| Prometheus + Grafana | 指标采集、可视化大盘 |
| 阿里云 ARMS | 应用实时监控 |
| 全链路追踪 | 网关→数据库链路追踪 |
| JVM 诊断 | 内存、线程、GC 分析 |

**关键洞察**：以前是运维的活 → 现在后端也要懂监控  
**简历价值**：有 Prometheus、Grafana、ARMS → 面试官觉得你有全局意识

---

## 07. 并发编程（面试重灾区）

| 知识点 | 要求 |
|--------|------|
| 异步编排 | `CompletableFuture`、`Stream API` |
| 锁机制 | `ReentrantLock`、`ReadWriteLock`、`Semaphore`、`CountDownLatch` |
| JMM | 内存模型、原子类、可见性、指令重排 |
| 线程池 | 线程池定制、`ForkJoinPool` 并行计算 |

**面试重点**：手写双重检查锁 + 线程池调参  
**通过率**：简历上有 Concurrent 包熟悉 → 能通过 80% Java 后端面试

---

## 08. 性能调优

| 方向 | 技能 |
|------|------|
| JVM 参数 | `-Xms/-Xmx`、GC 算法选择（G1、ZGC） |
| SQL 优化 | 慢查询日志、执行计划分析 |
| 压测 | JMeter、系统瓶颈分析 |
| 线上问题 | 能独立排查 CPU 100%、内存泄漏 |

---

## 09. 安全相关

| 方向 | 技能 |
|------|------|
| 漏洞防范 | SQL 注入、XSS、CSRF |
| 认证授权 | JWT、OAuth2.0、RBAC |
| 加密 | 敏感数据加密传输、存储 |
| 安全框架 | Spring Security |

---

## 10. AI 编程提效（2026必备）

| 工具/模式 | 要求 |
|-----------|------|
| AI 编程工具 | Cursor / Claude Code / GitHub Copilot 全栈项目开发 |
| AI 编程模式 | Vibe Coding、SDD、Harness Engineering |
| 辅助工具 | Spec-Kit、OpenSpec 驱动 AI 完成大型项目 |

---

## 11. AI 应用开发（Part 05）

| 方向 | 技能 |
|------|------|
| AI 框架 | Spring AI、LangChain4j |
| RAG 应用 | 向量数据库（PGvector）、文档 ETL、向量检索 |
| 智能体 | 工具调用、MCP、多 Agent 协作 |
| Prompt 工程 | Prompt 优化技巧 |
| 企业级 | 独立开发企业级 AI 智能体应用 |

---

## 总结

| 维度 | 核心要点 |
|------|----------|
| **基础** | Java 语言、Spring 生态、数据库、缓存 |
| **进阶** | 并发编程、性能调优、监控告警 |
| **工程** | 容器化、微服务、安全防护 |
| **趋势** | AI 编程提效、AI 应用开发 |

> **一句话总结**：后端基本盘扎实，再叠加 AI 能力，才是 2026 年的核心竞争力。

---

## 学习建议

1. **优先级**：01-05 是基本盘 → 必须掌握
2. **面试重点**：07 并发编程、02 Spring 原理
3. **加分项**：06 监控、11 AI 应用开发
4. **AI 工具**：10 的 AI 编程工具能大幅提升学习效率
