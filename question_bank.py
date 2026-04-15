test = {
  "Python_Algorithm_Engineer": {
    "definition": "专注于机器学习模型开发、数据挖掘及底层算法实现。",
    "question_bank": [
      {
        "id": "p1",
        "type": "technical",
        "question": "请解释 Transformer 中 Self-Attention 的时间复杂度，并说明为什么需要多头机制？",
        "answer_key": "复杂度为平方级与维度乘积，多头是为了在不同子空间捕捉特征。"
      },
      {
        "id": "p2",
        "type": "scenario",
        "question": "当模型推理延迟过高，无法满足实时业务需求时，你会从哪些维度进行压缩？",
        "answer_key": "量化, 模型剪枝, 蒸馏, 模型架构优化, 硬件加速"
      },
      {
        "id": "p3",
        "type": "technical",
        "question": "在训练深度学习模型时遇到梯度消失或梯度爆炸，你会采取哪些策略？",
        "answer_key": "权重初始化, 使用 Batch Normalization, 使用 ReLU 等激活函数, 梯度裁剪, 残差连接"
      },
      {
        "id": "p4",
        "type": "scenario",
        "question": "如果你的模型在验证集上效果很好，但在生产环境的真实数据上表现极差，你会如何排查这个问题？",
        "answer_key": "检查训练数据与真实数据分布差异, 检查特征处理逻辑是否一致, 数据泄露检查, 模型过拟合问题, 评估指标的选择是否合理"
      },
      {
        "id": "p5",
        "type": "behavior",
        "question": "当业务方对算法模型的“可解释性”提出质疑时，你通常如何向非技术人员解释黑盒模型的决策过程？",
        "answer_key": "利用可视化工具, 使用特征归因方法, 简化模型, 结合业务逻辑进行案例对比分析"
      },
      {
        "id": "p6",
        "type": "technical",
        "question": "在大模型微调过程中，低秩适配技术相比全参数微调有哪些优势？它是如何实现的？",
        "answer_key": "优势是参数量小，存储开销低；原理是在原始预训练权重旁通过低秩矩阵进行旁路训练，推理时合并权重。"
      },
      {
        "id": "p7",
        "type": "scenario",
        "question": "如果生产环境中的模型指标随时间出现明显的性能漂移，你会设计怎样的监控和自动更新机制？",
        "answer_key": "监控预测分布变化与业务指标阈值；设置自动触发更新阈值；建立线上评估流水线；引入对比实验进行新旧模型验证；实现版本控制与快速回滚。"
      },
      {
        "id": "p8",
        "type": "technical",
        "question": "为什么在进行梯度下降时需要对特征进行标准化或归一化？",
        "answer_key": "防止收敛速度差异大导致的震荡；避免数值溢出；提高损失函数表面的平滑度，使梯度下降路径更直观，加快收敛速度。"
      },
      {
        "id": "p9",
        "type": "technical",
        "question": "在分布式训练中，数据并行与模型并行有什么区别？当显存无法容纳单卡模型时你会如何处理？",
        "answer_key": "数据并行处理不同批次数据，模型并行将网络切分到不同显卡；显存不足时采用流水线并行、张量并行或优化内存管理技术。"
      },
      {
        "id": "p10",
        "type": "technical",
        "question": "请解释深度学习中的激活函数的作用。为什么现代神经网络较少使用 Sigmoid 而更倾向于使用 ReLU 或 Swish？",
        "answer_key": "激活函数引入非线性映射；Sigmoid 在深层网络易导致梯度消失且计算复杂，ReLU 计算效率高且能缓解梯度消失，Swish 能够平滑曲线提升模型泛化。"
      },
      {
        "id": "p11",
        "type": "scenario",
        "question": "如果在分类任务中发现数据集存在严重的类别不平衡问题，你会从哪些方面进行处理？",
        "answer_key": "数据层面采用重采样技术；模型层面调整损失函数权重或使用焦点损失函数聚焦难样本；评估层面摒弃单一准确率，转向使用精确率、召回率、F1 分数或 AUC 面积进行综合评估。"
      },
      {
        "id": "p12",
        "type": "technical",
        "question": "请解释什么是注意力机制中的残差连接与层归一化？它们在深层网络中起什么作用？",
        "answer_key": "残差连接通过跨层传递梯度防止退化，层归一化通过规范化层输入分布稳定训练过程；两者结合能有效加速收敛并训练更深的网络。"
      },
      {
        "id": "p13",
        "type": "scenario",
        "question": "当你需要将一个大型复杂模型部署到边缘设备，但该设备算力极度受限，你会采取哪些极端优化手段？",
        "answer_key": "进行低位量化，结合轻量化架构搜索，采用知识蒸馏将复杂模型能力迁移至精简网络，通过算子融合减少访存次数。"
      },
      {
        "id": "p14",
        "type": "technical",
        "question": "请简单描述损失函数的作用，并解释回归任务与分类任务通常分别使用什么损失函数？",
        "answer_key": "损失函数度量预测值与真实值的差异；回归任务常用均方误差，分类任务常用交叉熵损失。"
      },
      {
        "id": "p15",
        "type": "behavior",
        "question": "在项目开发周期紧张的情况下，你是如何在保证算法效果与项目进度之间进行平衡的？",
        "answer_key": "采用敏捷开发模式；优先搭建基线模型评估可行性；分阶段交付，先满足核心需求；利用开源预训练模型快速验证方案。"
      },
      {
        "id": "p16",
        "type": "technical",
        "question": "请解释什么是过拟合？除了增加数据量外，还有哪些常用方法可以缓解过拟合？",
        "answer_key": "过拟合指模型在训练集上表现优异但在测试集上表现较差；常用方法包括正则化、Dropout、早停机制、数据增强、简化模型结构。"
      },
      {
        "id": "p17",
        "type": "scenario",
        "question": "在推荐系统中，你是如何处理长尾效应的？",
        "answer_key": "通过曝光权重调整；在损失函数中引入重加权机制；引入内容特征以增强对新物品的推荐；使用多样性重排算法提升长尾物品可见度。"
      },
      {
        "id": "p18",
        "type": "technical",
        "question": "简述 Transformer 中位置编码的意义，以及为什么相对位置编码相比绝对位置编码在长文本任务中更具优势？",
        "answer_key": "位置编码为无序的注意力机制提供位置信息；绝对位置编码受限于训练长度，外推性差；相对位置编码关注词间相对距离，更符合语言逻辑，具有更好的长度外推能力。"
      },
      {
        "id": "p19",
        "type": "technical",
        "question": "请解释什么是蒙特卡洛树搜索（MCTS）？在强化学习中它如何通过模拟辅助决策？",
        "answer_key": "包含选择、扩展、模拟、回溯四个阶段；通过多次随机模拟预估节点胜率，平衡开发与探索，实现高效最优路径决策。"
      },
      {
        "id": "p20",
        "type": "technical",
        "question": "在编写矩阵乘法时，为什么简单的三层循环效率很低？从内存访问局部性（Cache Locality）的角度，你会如何优化？",
        "answer_key": "三层循环导致频繁跳跃访问内存，Cache 不命中率高。优化手段是采用分块技术，将大矩阵划分为小块放入 Cache，使数据访问更连续，减少缓存缺失。"
      },
      {
        "id": "p21",
        "type": "technical",
        "question": "为什么逻辑回归不使用均方误差作为损失函数，而选择对数似然损失（交叉熵）？从模型训练的角度谈谈原因。",
        "answer_key": "对数损失在梯度计算时会抵消掉 Sigmoid 的导数项，避免了梯度消失，且该损失函数是凸函数，利于梯度下降收敛到全局最优；均方误差会导致非凸优化，且梯度在预测值接近 0 或 1 时会趋于零，训练极其缓慢。"
      },
      {
        "id": "p22",
        "type": "technical",
        "question": "什么是 EM 算法？它在隐马尔可夫模型中起什么作用？",
        "answer_key": "包含求期望和最大化两步的迭代算法；用于存在隐变量的概率模型参数估计。在隐马尔可夫模型中，它对应 Baum-Welch 算法，通过迭代优化参数以拟合观测序列，是解决非监督序列标注问题的核心。"
      },
      {
        "id": "p23",
        "type": "scenario",
        "question": "如何设计一套模型在线评估系统，以确保模型更新后不会对核心指标造成负面影响？",
        "answer_key": "建立线上线下评估数据集；实施影子测试；进行小流量对比测试；监控核心业务指标报警；设计版本回滚逻辑。"
      },
      {
        "id": "p24",
        "type": "scenario",
        "question": "在涉及敏感数据的算法开发中，如何通过隐私计算提升数据安全性？",
        "answer_key": "使用差分隐私在样本中注入噪声；通过联邦学习实现数据可用不可见；利用同态加密进行密文计算；脱敏与匿名化处理。"
      },
      {
        "id": "p25",
        "type": "technical",
        "question": "请描述什么是 RAG（检索增强生成）？它相比直接微调大模型有哪些优势？",
        "answer_key": "通过外部知识库检索获取相关上下文，拼接至提示词引导生成；优势：缓解幻觉、知识实时更新快、部署成本低、无需频繁重训。"
      },
      {
        "id": "p26",
        "type": "technical",
        "question": "如何处理长文本窗口导致的显存瓶颈？请介绍几种针对长序列的 Attention 优化方案。",
        "answer_key": "FlashAttention 实现 IO 感知优化；Sparse Attention 稀疏化计算；Ring Attention 分布式并行；滑动窗口注意力机制。"
      },
      {
        "id": "p27",
        "type": "technical",
        "question": "在大模型推理优化中，为什么需要 KV Cache？它带来了什么代价？",
        "answer_key": "通过存储历史上下文的 Key 和 Value 避免重复计算；代价是占用大量显存，且随 Token 长度增加显存线性增长。"
      },
      {
        "id": "p28",
        "type": "technical",
        "question": "如何衡量一个机器学习模型的收敛状态？训练过程中 Loss 震荡剧烈可能由哪些原因导致？",
        "answer_key": "观察 Loss 与验证集指标是否趋于平稳；震荡原因：学习率过高、Batch Size 过小、数据标注噪声过大、网络初始化不佳。"
      },
      {
        "id": "p29",
        "type": "scenario",
        "question": "如果你在开发中发现算法模型“不可解释”引发了业务报错，你会如何实施应急排查？",
        "answer_key": "记录输入输出数据作为 Badcase；重现环境进行断点调试；分析特征权重是否有离群值；回滚模型版本至上一稳定态；人工介入规则过滤异常预测。"
      },
      {
        "id": "p30",
        "type": "behavior",
        "question": "你如何保持对前沿算法的持续学习？近期你关注过哪些最具突破性的技术或论文？",
        "answer_key": "通过 arXiv 阅读顶会论文；关注技术博客和开源社区；复现经典算法；定期总结技术趋势。"
      }
    ]
  },
  "Java_Backend_Engineer": {
    "definition": "后端服务开发，关注接口设计、并发、性能与系统可靠性。",
    "question_bank": [
      {
        "id": "j1",
        "type": "technical",
        "question": "请说明 Java 中的内存模型（JMM）对并发编程有什么影响？",
        "answer_key": "可见性, 有序性, 原子性, volatile, synchronized, happens-before"
      },
      {
        "id": "j2",
        "type": "scenario",
        "question": "在高并发场景下，如何设计接口以保证系统可伸缩？",
        "answer_key": "无状态服务, 负载均衡, 限流, 缓存, 异步化, 分布式追踪"
      },
      {
        "id": "j3",
        "type": "technical",
        "question": "在生产环境中，如何根据业务特性（如IO密集型 vs 计算密集型）来配置线程池参数？",
        "answer_key": "核心线程数计算公式, 阻塞队列类型, 饱和策略, 线程工厂, 动态线程池监控"
      },
      {
        "id": "j4",
        "type": "scenario",
        "question": "在高并发场景下，如何通过减小锁粒度或使用无锁编程来提升系统吞吐量？",
        "answer_key": "读写锁分离, ConcurrentHashMap分段锁, CAS乐观锁, 锁粗化, 线程本地变量"
      },
      {
        "id": "j5",
        "type": "technical",
        "question": "synchronized 关键字在 JDK 1.6 之后的锁升级过程是怎样的，为什么它依然是推荐的选择？",
        "answer_key": "偏向锁, 轻量级锁(自旋), 重量级锁, 锁消除, 锁粗化"
      },
      {
        "id": "j6",
        "type": "scenario",
        "question": "在 Web 服务器中使用 ThreadLocal 时，如果不及时清理会导致什么问题，如何防御？",
        "answer_key": "线程池复用, 内存泄漏, 弱引用机制, finally块中调用remove, 变量全生命周期管理"
      },
      {
        "id": "j7",
        "type": "technical",
        "question": "Java 中的 volatile 关键字是如何保证可见性和防止指令重排序的？",
        "answer_key": "内存屏障, 禁止指令重排, 强制刷新主存, 缓存一致性协议, happens-before原则"
      },
      {
        "id": "j8",
        "type": "technical",
        "question": "如果线上服务出现频繁的 Full GC，通常你会从哪些维度去定位根因？",
        "answer_key": "堆内存快照分析, 内存泄漏检测, 长生命周期对象, 元空间溢出, 检查 System.gc 调用"
      },
      {
        "id": "j9",
        "type": "scenario",
        "question": "在亿级流量场景下，如何根据业务特性选择最合适的垃圾回收器（如 G1、ZGC）？",
        "answer_key": "停顿时间要求, 吞吐量优先, 内存规模, 跨代引用处理, 调整堆参数"
      },
      {
        "id": "j10",
        "type": "technical",
        "question": "JVM 运行时内存区域划分中，哪些部分是线程私有的，哪些是线程共享的？它们对并发安全性有什么意义？",
        "answer_key": "程序计数器, 虚拟机栈, 本地方法栈, 堆, 方法区, 数据隔离"
      },
      {
        "id": "j11",
        "type": "scenario",
        "question": "如果系统在运行过程中出现明显的“内存抖动”（内存使用率忽高忽低），你认为可能的原因是什么？",
        "answer_key": "大对象分配, 频繁创建短生命周期对象, 新生代空间设置过小, 逃逸分析失效"
      },
      {
        "id": "j12",
        "type": "behavior",
        "question": "你曾经在优化 JVM 性能方面做过哪些具体的努力？请举例说明你的分析路径。",
        "answer_key": "GC 日志分析, 性能瓶颈采样, 指标对比, 堆栈跟踪, 参数调优效果验证"
      },
      {
        "id": "j13",
        "type": "technical",
        "question": "MySQL 索引为什么通常采用 B+ Tree 而不是 B Tree 或 Hash 索引？",
        "answer_key": "磁盘IO次数, 叶子节点链表结构, 范围查询效率, 顺序IO, 聚簇索引"
      },
      {
        "id": "j14",
        "type": "scenario",
        "question": "在电商库存扣减场景中，如何解决高并发下的数据一致性与超卖问题？",
        "answer_key": "数据库行锁, 乐观锁CAS, 分段锁, Redis预扣减, Lua脚本原子性"
      },
      {
        "id": "j15",
        "type": "technical",
        "question": "当数据库事务出现长事务时，为什么会引发严重的性能问题，如何监控和处理？",
        "answer_key": "回滚段堆积, 锁等待队列, 连接池耗尽, 慢SQL日志, 事务超时配置"
      },
      {
        "id": "j16",
        "type": "scenario",
        "question": "面对单表数据量过亿的情况，你会优先考虑哪些优化方案来保证接口响应速度？",
        "answer_key": "索引覆盖, 垂直拆分, 水平分库分表, 读写分离, ES检索辅助"
      },
      {
        "id": "j17",
        "type": "behavior",
        "question": "在处理线上慢查询报警时，你的排查思路和处理步骤通常是怎样的？",
        "answer_key": "执行计划分析, 索引命中率, 锁竞争排查, 慢日志分析, SQL重构"
      },
      {
        "id": "j18",
        "type": "technical",
        "question": "在分布式缓存场景中，如何解决“缓存击穿”与“缓存雪崩”问题？",
        "answer_key": "互斥锁, 逻辑过期, 设置过期时间随机化, 多级缓存, 限流熔断"
      },
      {
        "id": "j19",
        "type": "scenario",
        "question": "使用消息队列（如 Kafka/RocketMQ）保证分布式事务最终一致性时，如何确保消息不丢失且被幂等消费？",
        "answer_key": "生产者确认机制, 消息持久化, 幂等表, 数据库唯一约束, 手动ACK"
      },
      {
        "id": "j20",
        "type": "technical",
        "question": "分布式锁的实现中，基于 Redis (Redlock) 和基于 Zookeeper 的方案各有什么优缺点？",
        "answer_key": "AP与CP模型, 锁超时释放, 脑裂问题, Watch机制, 性能吞吐量"
      },
      {
        "id": "j21",
        "type": "scenario",
        "question": "在微服务拆分后，如何有效处理跨服务的数据一致性问题（不考虑强一致性场景）？",
        "answer_key": "Saga模式, TCC补偿事务, 本地消息表, 最终一致性, 异步回调"
      },
      {
        "id": "j22",
        "type": "technical",
        "question": "在高并发写入场景下，如何避免消息队列造成的“消息积压”问题？",
        "answer_key": "增加分区数, 扩容消费者实例, 批量处理, 降级丢弃非核心消息, 流量削峰"
      },
      {
        "id": "j23",
        "type": "technical",
        "question": "在 RPC 调用中，如何设计合理的超时机制以防止级联故障？",
        "answer_key": "连接超时与读超时区分, 熔断器配置, 链路超时时间传递, 默认超时设置, 异步请求非阻塞"
      },
      {
        "id": "j24",
        "type": "scenario",
        "question": "面对接口突发流量，你会采取哪些防御性策略来保证系统的稳定性？",
        "answer_key": "令牌桶/漏桶算法, 接口限流, 降级开关, 线程池隔离, 异步化处理"
      },
      {
        "id": "j25",
        "type": "technical",
        "question": "在开放平台设计 API 时，如何通过接口层面的设计保障数据安全性与请求唯一性？",
        "answer_key": "签名机制(Sign), 时间戳校验, 防重放Token, OAuth2, 敏感字段脱敏"
      },
      {
        "id": "j26",
        "type": "scenario",
        "question": "微服务之间的版本迭代频繁，如何优雅地处理接口兼容性问题（保持向下兼容）？",
        "answer_key": "字段扩展非删除, 版本号隔离, 默认值处理, 灰度发布, 契约测试"
      },
      {
        "id": "j27",
        "type": "behavior",
        "question": "如果你的某个依赖服务接口响应极其缓慢，你会采取什么治理手段保障你的核心业务可用？",
        "answer_key": "断路器熔断, 设置fallback兜底策略, 异步线程隔离, 监控报警, 降级非核心流程"
      },
      {
        "id": "j28",
        "type": "scenario",
        "question": "当系统在半夜发生大规模故障，且监控指标全线报警时，你的排查优先级顺序是什么？",
        "answer_key": "恢复业务可用性, 熔断隔离, 扩容/降级, 留存现场(dump), 根因分析"
      },
      {
        "id": "j29",
        "type": "technical",
        "question": "从单体应用向微服务架构演进时，如何规划数据库的拆分路径以降低风险？",
        "answer_key": "业务逻辑解耦, 读写分离, 垂直分库, 水平分库分表, 跨库事务解决方案"
      },
      {
        "id": "j30",
        "type": "scenario",
        "question": "在高并发系统的性能瓶颈排查中，如何判断瓶颈是在磁盘I/O、网络还是CPU计算？",
        "answer_key": "负载指标(Load Average), 磁盘队列深度(iowait), 网络吞吐(iftop), 线程CPU使用率, 火焰图"
      },
      {
        "id": "j31",
        "type": "behavior",
        "question": "请描述一次你经历过的最复杂的系统故障，你是如何通过技术手段定位并彻底解决它的？",
        "answer_key": "故障现象描述, 排查思路, 使用的工具, 根本原因, 改进措施与复盘"
      },
      {
        "id": "j32",
        "type": "technical",
        "question": "在大规模分布式集群中，如何设计一套能够支撑业务快速增长的技术方案？",
        "answer_key": "系统水平扩展, 服务自治, 全链路监控, 容灾建设, 标准化发布流程"
      }
    ]
  },
  "Web_Frontend_Engineer": {
    "definition": "前端工程与用户界面实现，关注性能、可访问性与跨端兼容性。",
    "question_bank": [
      {
        "id": "w1",
        "type": "technical",
        "question": "请解释浏览器的渲染流程（从 HTML 到页面呈现）以及影响渲染性能的因素。",
        "answer_key": "解析 HTML, 构建 DOM, CSSOM, render tree, layout, paint, compositing; 重排与重绘开销, 资源加载阻塞"
      },
      {
        "id": "w2",
        "type": "behavior",
        "question": "描述一次你处理跨浏览器兼容性问题的经历，你如何定位并解决的？",
        "answer_key": "定位问题, 回退策略, feature detection, polyfill, progressive enhancement"
      },
      {
        "id": "w3",
        "type": "technical",
        "question": "请描述从 URL 输入到页面渲染完成的全过程，哪些环节最影响首屏加载速度？",
        "answer_key": "DNS解析, TCP连接, HTTP请求/响应, HTML解析, 资源阻塞, 执行优先级, 重排重绘"
      },
      {
        "id": "w4",
        "type": "technical",
        "question": "页面性能指标（LCP, CLS, FID）是如何定义的？针对 CLS 你通常如何排查和优化？",
        "answer_key": "核心Web指标定义, 图片尺寸预设, 动态内容插入防抖, 字体加载优化"
      },
      {
        "id": "w5",
        "type": "scenario",
        "question": "在复杂的单页应用中，如何通过代码拆分（Code Splitting）和资源懒加载提升首屏体验？",
        "answer_key": "路由懒加载, 动态导入(import), 组件异步加载, 第三方库按需引入, Tree Shaking"
      },
      {
        "id": "w6",
        "type": "technical",
        "question": "浏览器的 Event Loop 如何协同宏任务与微任务？为什么过度使用 setTimeout 会阻塞渲染？",
        "answer_key": "宏任务, 微任务, 任务队列优先级, 渲染时机, 帧率阻塞"
      },
      {
        "id": "w7",
        "type": "behavior",
        "question": "如果你发现线上页面在某些低端机型上出现严重卡顿，你会采用什么步骤进行性能诊断？",
        "answer_key": "Performance面板, 火焰图分析, 内存泄漏检测, 频繁长任务分析, 代码瘦身"
      },
      {
        "id": "w8",
        "type": "technical",
        "question": "JavaScript 中的原型链（Prototype Chain）是如何工作的？在组件库设计中，它有什么实际应用？",
        "answer_key": "__proto__与prototype, 原型查找链, 继承模式, 对象属性共享, 插件扩展机制"
      },
      {
        "id": "w9",
        "type": "technical",
        "question": "闭包（Closure）在前端开发中主要解决了什么问题？请列举一个会导致内存泄漏的闭包场景。",
        "answer_key": "作用域链保存, 私有变量封装, 函数工厂, 长周期引用导致的DOM节点无法回收"
      },
      {
        "id": "w10",
        "type": "scenario",
        "question": "在复杂的异步流程中（如并行请求、串行执行、竞争处理），你如何封装 Promise 以保证逻辑清晰？",
        "answer_key": "Promise.all/race/allSettled, async/await语法糖, 错误捕获处理, 异步取消机制"
      },
      {
        "id": "w11",
        "type": "technical",
        "question": "this 的指向问题在 ES6 的箭头函数引入后发生了什么改变？为什么在 React Class 组件中需要 bind(this)？",
        "answer_key": "动态作用域, 词法作用域, 箭头函数绑定上下文, React回调函数执行环境"
      },
      {
        "id": "w12",
        "type": "behavior",
        "question": "在阅读大型前端项目源码时，你是如何通过分析 JavaScript 执行上下文来定位 Bug 的？",
        "answer_key": "堆栈跟踪, 变量生命周期, 词法环境分析, 断点调试策略"
      },
      {
        "id": "w13",
        "type": "technical",
        "question": "请对比 React 的 Fiber 架构与 Vue 的响应式系统，它们分别如何优化视图更新性能？",
        "answer_key": "增量更新, 任务中断与恢复, 依赖收集, 响应式劫持, Virtual DOM 差异对比"
      },
      {
        "id": "w14",
        "type": "scenario",
        "question": "在大型前端应用中，如何设计跨组件的状态共享机制以避免 prop drilling（属性穿透）？",
        "answer_key": "Context API, 状态管理库(Redux/Pinia/Zustand), 组合模式, Render Props"
      },
      {
        "id": "w15",
        "type": "technical",
        "question": "React Hooks 的实现原理是什么？为什么不允许在循环、条件或嵌套函数中调用 Hook？",
        "answer_key": "链表结构, 顺序依赖, Fiber节点状态存储, 调用顺序一致性"
      },
      {
        "id": "w16",
        "type": "scenario",
        "question": "如何设计一个高可复用的 UI 组件（如 Table 或 Dialog），使其具备良好的扩展性和易用性？",
        "answer_key": "配置化驱动, 插槽(Slots)设计, 组合式 API, 外部受控/内部非受控, 样式隔离"
      },
      {
        "id": "w17",
        "type": "behavior",
        "question": "你如何评估一个前端组件的设计是否“足够健壮”？请谈谈你的重构思路。",
        "answer_key": "低耦合, 高内聚, 测试覆盖率, 边界情况处理, 单元测试, API一致性"
      },
      {
        "id": "w18",
        "type": "technical",
        "question": "Webpack/Vite 的 Tree Shaking 原理是什么？为什么在工程开发中要避免使用 CommonJS？",
        "answer_key": "ESM静态分析, 副作用标记(sideEffects), AST代码结构, 导出引用处理, 模块化标准差异"
      },
      {
        "id": "w19",
        "type": "scenario",
        "question": "当项目编译速度过慢时，你会从哪些维度进行优化？",
        "answer_key": "缓存机制(loader cache), 多线程构建(thread-loader), 资源过滤, 分包策略, 升级Vite/Esbuild"
      },
      {
        "id": "w20",
        "type": "technical",
        "question": "在 monorepo 架构中，如何有效地管理项目依赖并优化工作流？",
        "answer_key": "工作空间(Workspaces), 依赖版本统一, pnpm/lerna应用, 自动化发布流程, 任务并行化"
      },
      {
        "id": "w21",
        "type": "scenario",
        "question": "如何建立前端代码质量保障体系（Code Quality Assurance）？",
        "answer_key": "ESLint规则, Prettier格式化, Husky钩子, 提交信息规范, CI/CD自动检测"
      },
      {
        "id": "w22",
        "type": "scenario",
        "question": "在从 Webpack 迁移到 Vite 的过程中，如何处理 CommonJS 依赖、环境变量注入差异及静态资源路径映射？",
        "answer_key": "Rollup插件兼容转换, Node Polyfills补全, 环境变量.env处理, 路径别名映射, 增量迁移策略"
      },
      {
        "id": "w23",
        "type": "technical",
        "question": "HTTP/2 相比 HTTP/1.1 在性能上有哪些本质提升？它是如何解决“队头阻塞”问题的？",
        "answer_key": "多路复用, 二进制分帧, 首部压缩(HPACK), 服务器推送, 优先级控制"
      },
      {
        "id": "w24",
        "type": "scenario",
        "question": "在复杂的单页应用中，如何设计一套完善的鉴权方案（如 JWT）并处理 Token 过期与刷新？",
        "answer_key": "Access Token与Refresh Token, 无感刷新, 拦截器处理, 存储方案(Cookie/LocalStorage), 退出登录清理"
      },
      {
        "id": "w25",
        "type": "technical",
        "question": "谈谈对浏览器安全策略（CSP, CORS, SameSite）的理解，它们如何防御常见的注入攻击？",
        "answer_key": "限制资源来源(CSP), 跨域资源共享(CORS), Cookie安全属性, 防御XSS与CSRF"
      },
      {
        "id": "w26",
        "type": "scenario",
        "question": "当遇到跨域请求时，除了 CORS，你还知道哪些解决方案？各自适用场景是什么？",
        "answer_key": "JSONP(老旧方案), Nginx代理, PostMessage, WebSocket, 跨域资源共享(CORS)配置"
      },
      {
        "id": "w27",
        "type": "behavior",
        "question": "如果线上监控发现大量前端错误日志（如 404, 500, 脚本报错），你的紧急排查链路是怎样的？",
        "answer_key": "错误日志聚合(Sentry/监控平台), SourceMap还原, 定位网络链路, 灰度回滚, 差异对比分析"
      },
      {
        "id": "w28",
        "type": "scenario",
        "question": "在跨端（Web/小程序/App）项目开发中，如何处理不同环境下的原生能力差异与表现一致性？",
        "answer_key": "抽象层封装(适配器模式), 条件编译, 桥接通信协议(Bridge), 环境探测, 统一UI库与主题系统"
      },
      {
        "id": "w29",
        "type": "technical",
        "question": "当业务量庞大导致前端构建时间过长或部署失败时，如何进行全流程架构演进？",
        "answer_key": "微前端架构(Micro-frontend), 联邦模块(Module Federation), 增量部署, 构建流水线并行化"
      },
      {
        "id": "w30",
        "type": "behavior",
        "question": "如果你需要向非技术团队（如产品/业务方）解释某个技术债务（如重构组件库）的必要性，你会如何沟通？",
        "answer_key": "成本效益分析, 用户体验影响(性能), 开发效率指标, 风险预警, 达成共识与排期"
      },
      {
        "id": "w31",
        "type": "scenario",
        "question": "如何设计一套前端监控系统，用以全链路追踪用户行为、性能指标及异常数据？",
        "answer_key": "埋点采集方案, 性能指标上报, 错误拦截与快照, 溯源日志, 数据可视化看板"
      },
      {
        "id": "w32",
        "type": "behavior",
        "question": "作为十年资深前端，你认为当下技术选型的核心原则是什么？如何看待“技术过剩”现象？",
        "answer_key": "业务场景优先, 社区生态活跃度, 团队技术储备, 可维护性与演进成本, 拒绝盲目追新"
      }
    ]
  }
}