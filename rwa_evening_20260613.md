# 链上美股的"最后一公里"终于打通了——SEC 动刀 Reg NMS，代币化股票的合规枷锁正在脱落

## RWA 时评 | 2026-06-13

### 文章解读

2026 年 6 月 12 日，SEC 正式发布提案，拟废除 Regulation NMS 中已实施近 20 年的 Rule 611（交易穿透禁止）和 Rule 610(e)（锁定/交叉报价保护）。这两条规则是 AMM 等链上交易机制进入美国证券市场的最大合规屏障——它们的废除，意味着代币化美股在 DeFi 平台上合法交易的结构性障碍正在被移除。几乎同一时间，西班牙批发托管银行 Cecabank 在 MiCA 框架下正式上线加密资产托管服务，管理资产超 4000 亿欧元，为欧洲传统金融机构接入加密生态提供了标准化的 B2B 模板。

一边是监管层主动拆墙，一边是机构在合规框架下加速入场——这两件事放在一起看，RWA 赛道的底层逻辑正在发生质变：不再是"能不能合规"的问题，而是"合规路径已经铺好，谁先上车"的问题。

---

### SEC 动刀 Reg NMS：为什么这条规则是链上美股的"死锁"

**Rule 611 和 Rule 610(e) 到底管什么？**

这两条规则是 2005 年生效的全国市场系统监管规则（Regulation NMS）的核心条款，运行了将近 20 年，是美国股票市场交易架构的底层约束：

| 规则 | 核心要求 | 实施年份 |
|------|---------|---------|
| Rule 611（Order Protection Rule） | 禁止以劣于全市场最优报价（NBBO）的价格执行交易，即"交易穿透禁令" | 2005 |
| Rule 610(e) | 禁止交易中心展示与其他交易所最优报价形成锁定或交叉的报价 | 2005 |

在传统集中式交易所的语境下，这两条规则逻辑自洽——确保投资者始终获得全市场最优价格，防止交易所之间报价错配。但问题出在 DeFi 的交易机制上。

**AMM 为什么天然违规？**

去中心化金融的核心交易机制——自动做市商（AMM）——与这两条规则存在根本性冲突：

1. **AMM 无法实时匹配 NBBO。** AMM 基于联合曲线（bonding curve）设定价格，在出块时间间隔内执行交易，无法像传统交易所那样以亚毫秒级速度获取全市场最优报价并实时调整。这意味着，当纳斯达克某只股票的买入价高于 AMM 池中的卖出价时，AMM 仍然会按照自身算法执行——这在 Rule 611 下就是"交易穿透"违规。

2. **AMM 的报价天然会产生锁定/交叉。** AMM 按区块时间而非毫秒级频率更新价格，常规性地与 NBBO 出现锁定或交叉。在 Rule 610(e) 下，这种行为直接构成违规，交易平台可能因此失去合规资质。

Galaxy Digital 研究主管 Alex Thorn 的判断一针见血：**"代币化 NMS 股票的任何资金池都会持续出现交易穿透，几乎可以肯定会被认定为非法交易场所。"** 这不是技术不够好的问题，而是规则本身不兼容链上交易逻辑。

**提案的核心：拆墙换框架**

SEC 提案的核心举措分为两层：

| 层次 | 内容 |
|------|------|
| 拆除 | 正式废除 Rule 611 和 Rule 610(e)，消除 AMM 等链上机制的结构性合规障碍 |
| 替换 | 转向 FINRA Rule 5310 的"最佳执行"原则框架 |

FINRA Rule 5310 与旧规则的根本区别在于：它是**原则导向**（principles-based）而非**规则导向**（rules-based）的。旧 Rule 611 是逐笔检查每笔交易是否优于 NBBO——这对 AMM 来说不可能实现。而 Rule 5310 是从整体执行质量、速度、订单规模等多维度综合评估经纪商是否履行了"最佳执行"义务，**能够以当前 NMS 规则无法做到的方式兼容自动做市商**。

这不是放松监管，而是换了一套适配链上交易逻辑的监管语言。

**时间线与关键节点**

| 时间 | 事件 |
|------|------|
| 2025 年 8 月 | SEC 启动"Project Crypto"框架，为美国资本市场数字资产制定监管指导 |
| 2026 年 6 月 12 日 | SEC 正式发布 267 页提案，开启 60 天公众意见征询期 |
| 2027 年 Q1（预计） | 最终规则预计正式生效 |
| 规则生效前（预计） | SEC 可能对早期代币化试点项目发放 Rule 611 的豁免许可（exemptive relief） |

SEC 主席 Paul Atkins 对提案的定位非常清晰：**"简化市场结构，降低市场参与者的成本，让竞争和创新塑造股票市场的持续演进。"** TD Cowen 华盛顿研究组董事总经理 Jaret Seiberg 判断，该提案通过概率很高，且废除这两条规则一直是 Atkins 的长期优先事项。

**仍然存在的障碍**

废除 Rule 611 和 610(e) 是最大的结构性解锁，但不是终点。代币化美股仍需解决：

- 交易所或替代交易系统（ATS）注册要求
- 清算和结算安排
- 多项未针对去中心化或点对点交易场景编写的存量规则

SEC 已表示将考虑通过"创新豁免"（innovation exemption）机制逐步解决这些遗留问题。Alex Thorn 将本次废除视为通过创新豁免解决交易场所注册问题的**前期准备**——先把最大的结构性障碍拆掉，再逐个清理剩余的合规死角。

---

### Cecabank 上线 MiCA 托管：传统金融入场的标准化模板

就在 SEC 动刀 Reg NMS 的几乎同一时间，欧洲也在用自己的方式推进传统金融与加密生态的融合。

**西班牙银行业的合规样本**

2026 年 6 月 11 日，西班牙批发托管银行 Cecabank 正式上线加密资产托管服务，面向银行、券商、财富管理机构等金融机构提供 B2B 服务。这不是一个实验性项目——Cecabank 管理资产超过 **4000 亿欧元**，服务 100+ 金融机构，覆盖 70+ 国际市场。

| 指标 | 数据 |
|------|------|
| 管理资产规模 | 超过 4000 亿欧元 |
| 服务金融机构 | 100+ 家 |
| 覆盖市场 | 70+ 个国际市场 |
| 技术合作方 | Bit2Me（日现货交易量超 2.8 亿美元） |
| 首个客户 | Renta 4 Banco |

**双重注册：合规的"两个第一"**

Cecabank 的合规路径体现了 MiCA 框架下传统金融机构入场的标准范式：

| 注册节点 | 时间 | 意义 |
|---------|------|------|
| 西班牙银行 CASP 注册 | 2024 年 11-12 月 | 西班牙**唯一**以此身份注册的金融机构 |
| CNMV MiCA 许可 | 2025 年 7 月 | **首家**获得此授权的 B2B 托管机构 |

服务许可范围涵盖托管、指令接收与传输（RTO）、转账三项核心业务。

**B2B 模式的关键设计**

Cecabank 的方案不是一个直接面向零售用户的产品，而是一个**金融机构即服务**（Institution-as-a-Service）的基础设施：

- **Cecabank**：提供技术基础设施、机构级托管、合规流程，采用与传统证券业务等效的安全标准
- **Bit2Me**：提供交易执行平台、流动性、市场接入，持有 ISO 27001/22301/37001/37301 等多项认证
- **Renta 4 Banco**：作为首个客户，通过 Cecabank 的端到端方案为自身终端客户提供加密交易服务

这种分工意味着：中小银行和券商无需自建技术体系、无需独立承担合规适配成本，即可进入加密资产领域。Cecabank 证券服务企业总监 Aurora Cuadros 的定位很精准：**"作为传统领域托管服务的标杆提供商，我们正在迈出自然的一步，将经验和标准转移到数字资产世界。"**

**欧洲护照化：从西班牙到全欧**

MiCA 的核心制度优势在于"护照化"——一旦在一个成员国获得许可，即可在欧盟全境提供服务，无需逐国申请。Cecabank 已经启动了爱尔兰、葡萄牙、卢森堡三国的护照化程序，并在卢森堡开设办事处、加入当地银行协会董事会。

| 扩张阶段 | 目标市场 | 状态 |
|---------|---------|------|
| 第一阶段 | 西班牙 | 已上线 |
| 第二阶段 | 爱尔兰、葡萄牙、卢森堡 | 护照化程序进行中 |

**全球竞争格局**

Cecabank 的动作不是孤例，而是全球传统金融机构入场加密托管的大趋势的一个切面：

| 地区 | 动态 |
|------|------|
| 美国 | OCC/美联储/FDIC 于 2025 年 7 月联合确认全国性银行可在适当风险管理下提供加密托管；前 25 大银行中 60% 已推出或宣布 BTC 产品 |
| 美国 | 摩根大通、富国银行、花旗等积极开发加密服务；花旗称其为"关键任务" |
| 英国 | 渣打银行计划收购 Zodia Custody |
| 西班牙 | BBVA 已试点由银行直接管理的 BTC/ETH 交易与托管 |
| 美国 | 明尼苏达州授权州特许银行自 2026 年 8 月起托管数字资产 |

Bit2Me 银行解决方案总监 Gabriel Ayela 的判断值得注意：**"这种联盟证实西班牙正在引领数字资产融入欧洲金融部门的实际进程。"** 不过，美国银行业的加速入场意味着欧洲的先发优势正在被快速侵蚀——合规确定性是欧洲的牌，资本和客户规模是美国的牌。

---

### 对从业者的一些启示

**1. SEC 拆墙的速度超出预期——代币化美股的基础设施窗口已经打开**

Rule 611 的废除不是会不会的问题，而是什么时候的问题。TD Cowen 判断 2027 年 Q1 落地是大概率事件，且 SEC 可能在正式规则出台前就对试点项目发放豁免许可。这意味着：从现在开始到 2027 年 Q1，是代币化美股基础设施的黄金布局期。做 AMM 协议、做链上清算结算、做代币化股票发行技术的团队，应该立即启动合规对话，争取成为首批豁免试点。等到规则正式落地再入场，格局已经定了。

**2. 监管语言从"规则导向"转向"原则导向"——这是全球趋势**

SEC 用 FINRA Rule 5310 的"最佳执行"原则替换 Rule 611 的逐笔检查，逻辑与 MiCA 的原则导向框架一致：不规定具体的技术实现路径，而是设定结果导向的合规标准。对从业者来说，这意味着合规策略要从"如何满足每一条具体规则"转向"如何在原则框架下证明自己的执行质量"。后者更灵活，但也更需要主动建立可审计的执行质量证据链。

**3. MiCA 护照化是欧洲市场的结构性红利——但窗口期有限**

Cecabank 从西班牙银行 CASP 注册到上线服务花了约 18 个月，护照化又需要额外时间。这意味着：先拿到 MiCA 牌照的机构有 12-18 个月的先发窗口，可以在竞争对手完成护照化之前率先覆盖多个欧盟市场。对于计划进入欧洲市场的 RWA/加密项目，选择已有 MiCA 牌照的 B2B 托管机构作为合作伙伴，比自己申请牌照的上市时间至少快一年。

**4. B2B2C 托管模式正在成为传统金融入场的标准路径**

Cecabank 的模式——B2B 托管基础设施 + 技术合作方提供交易能力 + 金融机构作为面向客户的入口——正在成为全球模板。美国银行端也在走类似路径（NYDIG 与社区银行的合作就是美国版）。做 RWA 发行或交易的项目方，与其试图直接获取终端用户，不如先嵌入这种 B2B2C 链条，成为传统金融机构的加密能力供应商。

**5. 两件事放在一起看：合规路径正在两条赛道同时铺开**

SEC 动刀 Reg NMS 解决的是"链上交易是否合法"的问题——拆掉存量规则的结构性障碍。Cecabank 上线 MiCA 托管解决的是"传统金融机构如何入场"的问题——在合规框架下提供基础设施。两条路径同时推进，指向同一个终点：RWA 赛道的合规基础设施正在成型，2026-2027 年是从"能不能做"到"谁做得更快"的转折期。从业者需要同时关注两个维度——既要理解监管拆墙带来的新机会，也要建立与传统金融机构合作的渠道能力。

---

*本文分析基于 2026 年 6 月 12-13 日的公开报道。*
*新闻来源：*
1. [Blockonomi - SEC Proposes Eliminating Trading Rules That Blocked Tokenized Stocks on DeFi Platforms](https://blockonomi.com/sec-proposes-eliminating-trading-rules-that-blocked-tokenized-stocks-on-defi-platforms/)
2. [CryptoTimes - SEC Proposes Scrapping Legacy Reg NMS Rules, Clearing Path for On-Chain Equities](https://www.cryptotimes.io/2026/06/12/sec-proposes-scrapping-legacy-reg-nms-rules-clearing-path-for-on-chain-equities/)
3. [The Coinomist - SEC Proposal to Free Tokenized U.S. Stocks for DeFi](https://thecoinomist.com/news/sec-rescind-nms-rules-611-610-enable-tokenized-us-stocks-defi/)
4. [CoinUnited - SEC Proposes Scrapping NMS Trade-Through Rules: A Structural Unlock](https://coinunited.io/en/pulse/2026-06-12/sec-proposes-scrapping-nms-trade-through-rules-a-structural-unlock-for-tokenized-us-stocks-and-eth-layer-infrastructure)
5. [SEC.gov - Proposed Rule: The Trade-Through Rule and Locked and Crossed Markets](https://www.sec.gov/files/rules/proposed/2026/34-105655.pdf)
6. [Blockonomi - Cecabank Brings MiCA-Regulated Crypto Custody to Spanish Banks](https://blockonomi.com/cecabank-brings-mica-regulated-crypto-custody-to-spanish-banks/)
7. [PRNewswire - Cecabank Launches Cryptocurrency Asset Custody Service](https://www.prnewswire.com/news-releases/cecabank-launches-cryptocurrency-asset-custody-service-with-its-first-client-in-collaboration-with-bit2me-302797013.html)
8. [CoinAlertNews - Cecabank Launches Crypto Custody, Joining Global Bank Push](https://coinalertnews.com/news/2026/06/11/cecabank-crypto-custody-launch)
