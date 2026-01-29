-- Knowledge Graph Book Recommendation System Initialization Script
-- Generated on 2026-01-03 14:33:14

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- CREATE DATABASE IF NOT EXISTS book_rec_sys;
-- USE book_rec_sys;

-- Drop existing tables
DROP TABLE IF EXISTS `search_logs`;
DROP TABLE IF EXISTS `interactions`;
DROP TABLE IF EXISTS `ratings`;
DROP TABLE IF EXISTS `books`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `users`;

-- Create tables
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_superuser` tinyint(1) DEFAULT '0',
  `gender` varchar(10) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `preferred_categories` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_categories_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `books` (
  `id` int NOT NULL AUTO_INCREMENT,
  `isbn` varchar(20) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `publisher` varchar(255) DEFAULT NULL,
  `publication_year` int DEFAULT NULL,
  `description` text,
  `cover_url` varchar(500) DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `average_rating` float DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_books_isbn` (`isbn`),
  KEY `ix_books_title` (`title`),
  KEY `ix_books_author` (`author`),
  KEY `fk_books_categories` (`category_id`),
  CONSTRAINT `fk_books_categories` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ratings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `rating` int NOT NULL,
  `comment` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_ratings_id` (`id`),
  KEY `fk_ratings_users` (`user_id`),
  KEY `fk_ratings_books` (`book_id`),
  CONSTRAINT `fk_ratings_books` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`),
  CONSTRAINT `fk_ratings_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `interactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `book_id` int NOT NULL,
  `interaction_type` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_interactions_id` (`id`),
  KEY `fk_interactions_users` (`user_id`),
  KEY `fk_interactions_books` (`book_id`),
  CONSTRAINT `fk_interactions_books` FOREIGN KEY (`book_id`) REFERENCES `books` (`id`),
  CONSTRAINT `fk_interactions_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `search_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `query` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_search_logs_id` (`id`),
  KEY `fk_search_logs_users` (`user_id`),
  CONSTRAINT `fk_search_logs_users` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert Categories
INSERT INTO `categories` (`id`, `name`) VALUES (1, '科幻');
INSERT INTO `categories` (`id`, `name`) VALUES (2, '历史');
INSERT INTO `categories` (`id`, `name`) VALUES (3, '计算机');
INSERT INTO `categories` (`id`, `name`) VALUES (4, '经济管理');
INSERT INTO `categories` (`id`, `name`) VALUES (5, '心理学');
INSERT INTO `categories` (`id`, `name`) VALUES (6, '悬疑');

-- Insert Users
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `is_active`, `is_superuser`) VALUES (1, 'user1', 'user1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzvPpYkV8A.6J.6J.6J.6J.', 1, 0);
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `is_active`, `is_superuser`) VALUES (2, 'user2', 'user2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzvPpYkV8A.6J.6J.6J.6J.', 1, 0);
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `is_active`, `is_superuser`) VALUES (3, 'user3', 'user3@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn96pzvPpYkV8A.6J.6J.6J.6J.', 1, 0);

-- Insert Books
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (1, '9787536692930', '三体', '刘慈欣', '文化大革命如火如荼进行的同时，军方探寻外星文明的绝秘计划“红岸工程”取得了突破性进展。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (2, '9787536692931', '球状闪电', '刘慈欣', '某个离奇的雨夜，一颗球状闪电闯进了少年的视野。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (3, '9787539953250', '银河帝国：基地', '阿西莫夫', '人类蜗居在银河系的一个小角落——太阳系，在围绕太阳旋转的第三颗行星上，生活了十多万年之久。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (4, '9787201124698', '沙丘', '弗兰克·赫伯特', '哥白尼提出了日心说，我们才知道世界并不是宇宙的中心。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (5, '9787536687868', '海伯利安', '丹·西蒙斯', '28世纪，地球已被黑洞吞噬，人类在银河系中建立了霸主政权。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (6, '9787536693968', '黑暗森林', '刘慈欣', '三体人在利用科技锁死了地球人的科学之后，出动庞大的宇宙舰队直扑太阳系。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (7, '9787536693969', '死神永生', '刘慈欣', '与三体文明的战争使人类第一次看到了宇宙黑暗的真相。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (8, '9787532731183', '银河系漫游指南', '道格拉斯·亚当斯', '地球被毁灭了，因为要在它所在的地方修建一条超空间快速通道。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (9, '9787530004951', '安德的游戏', '奥森·斯科特·卡德', '可怕的外星怪物——虫族越来越严厉地威胁着地球。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (10, '9787560086880', '雪崩', '尼尔·斯蒂芬森', '只有送披萨的，才能在这个混乱的世界里来去自如。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (11, '9787532763788', '神经漫游者', '威廉·吉布森', '他曾是网络空间最顶尖的黑客。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (12, '9787544715870', '仿生人会梦见电子羊吗？', '菲利普·K·迪克', '核战后，放射尘让地球上的动物濒临灭绝。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (13, '9787208157774', '2001：太空漫游', '亚瑟·克拉克', '一块神秘的黑色石板在史前时代启蒙了人类的祖先。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (14, '9787544758501', '火星救援', '安迪·威尔', '六天前，马克·沃特尼成为了第一批行走在火星上的人。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (15, '9787532729784', '星船伞兵', '罗伯特·海因莱因', '高中毕业时，你可以选择继续上学，或去参军。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (16, '9787539965000', '永恒的终结', '阿西莫夫', '24世纪，人类发明了时间力场。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (17, '9787544711391', '索拉里斯星', '斯坦尼斯瓦夫·莱姆', '索拉里斯星是一颗围绕双星运转的行星。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (18, '9787544265542', '从地球到月球', '凡尔纳', '巴尔的摩大炮俱乐部主席巴比康提议向月球发射一颗炮弹。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (19, '9787544265535', '海底两万里', '凡尔纳', '博物学家阿龙纳斯教授受邀参与追捕这只“怪物”。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (20, '9787544766865', '美丽新世界', '赫胥黎', '这是一个没有痛苦、没有烦恼、没有疾病、没有衰老的世界。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (21, '9787544711643', '1984', '乔治·奥威尔', '温斯顿生活在“大洋国”，这里只有一个党。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (22, '9787536694675', '流浪地球', '刘慈欣', '太阳即将毁灭，人类在地球表面建造出巨大的推进器。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (23, '9787536694682', '朝闻道', '刘慈欣', '为了探索宇宙的终极真理，人类可以付出什么代价？', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (24, '9787536694699', '乡村教师', '刘慈欣', '一位身患绝症的乡村教师，在生命的最后时刻。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (25, '9787536694705', '微纪元', '刘慈欣', '人类通过基因改造将身体缩小到细菌大小，以适应资源匮乏的地球。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (26, '9787544710899', '时间机器', 'H.G.威尔斯', '时间旅行者发明了一台机器，可以穿越时空。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (27, '9787544710905', '隐形人', 'H.G.威尔斯', '格里芬发现了一种可以将物体变得隐形的方法。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (28, '9787544710912', '世界大战', 'H.G.威尔斯', '火星人入侵地球，人类面临灭顶之灾。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (29, '9787201083988', '深渊上的火', '弗诺·文奇', '银河系被划分为不同的区域，在此区域之上是超光速的“飞跃界”。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (30, '9787201083995', '天渊', '弗诺·文奇', '青河舰队在太空中流浪，寻找着传说中的“天渊”。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (31, '9787201084008', '真名实姓', '弗诺·文奇', '在这个网络世界里，你的真名实姓就是你最大的弱点。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (32, '9787560086881', '溃雪', '尼尔·斯蒂芬森', '这是一种通过语言传播的病毒，可以感染人类的大脑。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (33, '9787560086882', '钻石年代', '尼尔·斯蒂芬森', '在这个纳米技术高度发达的时代，社会结构发生了巨大的变化。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (34, '9787508616476', '群', '弗兰克·施茨廷', '海洋中的生物开始联合起来，向人类发起攻击。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (35, '9787532745333', '接触', '卡尔·萨根', '艾莉·阿罗维博士截获了一组来自织女星的无线电信号。', 'https://via.placeholder.com/150', 1, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (36, '9787536692932', '明朝那些事儿', '当年明月', '这一系列书讲的是明朝的那些事。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (37, '9787101069740', '万历十五年', '黄仁宇', '万历十五年，亦即公元1587年。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (38, '9787301204689', '全球通史', '斯塔夫里阿诺斯', '本书是著名历史学家斯塔夫里阿诺斯的代表作。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (39, '9787508647357', '人类简史', '尤瓦尔·赫拉利', '十万年前，地球上至少有六种不同的人。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (40, '9787108009355', '中国历代政治得失', '钱穆', '本书为作者的专题演讲录。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (41, '9787208060364', '枪炮、病菌与钢铁', '贾雷德·戴蒙德', '为什么是欧亚大陆人征服、赶走或大批杀死印第安人、澳大利亚人和非洲人？', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (42, '9787108022682', '历史深处的忧虑', '林达', '本书以信件的形式，介绍了美国历史上的著名案件。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (43, '9787020124848', '大明王朝1566', '刘和平', '嘉靖四十年，国库亏空，民不聊生。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (44, '9787108041430', '叫魂', '孔飞力', '1768年，中国悲剧性近代的前夜。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (45, '9787100094663', '旧制度与大革命', '托克维尔', '探讨了法国大革命的起源、性质和影响。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (46, '9787100094762', '菊与刀', '露丝·本尼迪克特', '二战后期，美国为了研究日本，委托人类学家本尼迪克特撰写了这份报告。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (47, '9787508616490', '光荣与梦想', '威廉·曼彻斯特', '本书记录了从1932年罗斯福总统上台到1972年尼克松总统下台期间的美国历史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (48, '9787101103147', '史记', '司马迁', '中国第一部纪传体通史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (49, '9787101078780', '资治通鉴', '司马光', '中国第一部编年体通史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (50, '9787101003073', '三国志', '陈寿', '记载了魏、蜀、吴三国的历史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (51, '9787101003059', '汉书', '班固', '记载了西汉的历史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (52, '9787101003066', '后汉书', '范晔', '记载了东汉的历史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (53, '9787532746408', '罗马帝国衰亡史', '吉本', '本书是关于罗马帝国衰亡的历史巨著。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (54, '9787508616506', '第三帝国的兴亡', '威廉·夏伊勒', '本书详细记录了纳粹德国的兴起和灭亡。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (55, '9787544770282', '从大都到上都', '罗新', '作者徒步考察了元代连接大都和上都的辇路。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (56, '9787540488669', '显微镜下的大明', '马伯庸', '本书讲述了明朝基层的六个政治事件。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (57, '9787108022699', '天朝的崩溃', '茅海建', '本书对鸦片战争进行了详细的考证和分析。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (58, '9787108022705', '近代中国社会的新陈代谢', '陈旭麓', '本书对近代中国社会的变迁进行了深入的探讨。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (59, '9787530214640', '我们生活在巨大的差距里', '余华', '本书是余华近年来的杂文集。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (60, '9787532778003', '鱼翅与花椒', '扶霞·邓洛普', '一位英国人在中国的寻味之旅。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (61, '9787509780589', '撒马尔罕的金桃', '薛爱华', '本书研究了唐代的外来文明。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (62, '9787509780596', '万国一邦', '入江昭', '本书探讨了国际主义在近代历史中的演变。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (63, '9787508693835', '棉花帝国', '斯文·贝克特', '一部全球资本主义史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (64, '9787213075835', '丝绸之路', '彼得·弗兰科潘', '一部全新的世界史。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (65, '9787549556837', '历史的终结与最后的人', '弗朗西斯·福山', '本书探讨了自由民主制度是否是人类历史的终点。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (66, '9787500476481', '文明的冲突与世界秩序的重建', '亨廷顿', '本书认为冷战后的冲突主要是文明之间的冲突。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (67, '9787010059341', '大国崛起', '唐晋', '本书记录了九个大国的崛起过程。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (68, '9787508607733', '激荡三十年', '吴晓波', '记录了中国企业在改革开放三十年中的沉浮。', 'https://via.placeholder.com/150', 2, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (69, '9787115428028', 'Python编程：从入门到实践', 'Eric Matthes', '本书是一本针对所有层次的Python 读者而作的Python 入门书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (70, '9787111544937', '深入理解计算机系统', 'Randal E. Bryant', '程序员必读经典。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (71, '9787111407010', '算法导论', 'Thomas H. Cormen', '本书深入浅出地介绍了各种算法。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (72, '9787111599715', '计算机网络：自顶向下方法', 'James F. Kurose', '本书采用自顶向下的方法讲解计算机网络。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (73, '9787121022982', '代码大全', 'Steve McConnell', '本书介绍了软件构建的最佳实践。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (74, '9787302106199', '人月神话', 'Frederick P. Brooks Jr.', '软件工程领域的经典之作。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (75, '9787111075752', '设计模式', 'Erich Gamma', '本书介绍了23种常见的设计模式。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (76, '9787115508645', '重构', 'Martin Fowler', '改善既有代码的设计。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (77, '9787115216878', 'Clean Code', 'Robert C. Martin', '代码整洁之道。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (78, '9787121085116', '程序员的自我修养', '俞甲子', '链接、装载与库。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (79, '9787115351531', '图解HTTP', '上野宣', '本书对HTTP协议进行了通俗易懂的讲解。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (80, '9787115249494', '黑客与画家', 'Paul Graham', '硅谷创业教父Paul Graham的文集。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (81, '9787115262783', '浪潮之巅', '吴军', '梳理了IT产业发展的历史脉络。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (82, '9787115282828', '数学之美', '吴军', '本书介绍了数学在信息检索和自然语言处理中的应用。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (83, '9787115179289', '编程珠玑', 'Jon Bentley', '本书涵盖了程序员在实际工作中经常遇到的问题。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (84, '9787121123320', 'Effective C++', 'Scott Meyers', '改善程序与设计的55个具体做法。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (85, '9787111213826', 'Java编程思想', 'Bruce Eckel', 'Java领域的圣经。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (86, '9787115275790', 'JavaScript高级程序设计', 'Nicholas C. Zakas', 'JavaScript红宝书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (87, '9787111306361', '鸟哥的Linux私房菜', '鸟哥', '最受欢迎的Linux入门书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (88, '9787111436737', '利用Python进行数据分析', 'Wes McKinney', 'Pandas作者亲笔撰写。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (89, '9787302423287', '机器学习', '周志华', '西瓜书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (90, '9787115461476', '深度学习', 'Ian Goodfellow', '花书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (91, '9787302275954', '统计学习方法', '李航', '全面系统地介绍了统计学习的主要方法。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (92, '9787115454157', '流畅的Python', 'Luciano Ramalho', '致力于帮助Python开发人员挖掘这门语言及相关程序库的优秀特性。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (93, '9787115445353', 'Go语言实战', 'William Kennedy', 'Go语言的实战指南。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (94, '9787121323386', 'Kubernetes权威指南', '龚正', 'Kubernetes的百科全书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (95, '9787115417305', 'Spring实战', 'Craig Walls', 'Spring框架的经典教程。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (96, '9787111464747', 'Redis设计与实现', '黄健宏', '深入剖析Redis内部结构。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (97, '9787121198854', '高性能MySQL', 'Baron Schwartz', 'MySQL领域的经典之作。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (98, '9787115352118', 'Unix环境高级编程', 'W. Richard Stevens', 'Unix/Linux编程的圣经。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (99, '9787111135104', '计算机程序的构造和解释', 'Harold Abelson', 'SICP，计算机科学的经典教材。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (100, '9787111251217', '编译原理', 'Alfred V. Aho', '龙书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (101, '9787111627999', '操作系统导论', 'Remzi H. Arpaci-Dusseau', 'OSTEP，一本关于操作系统的书。', 'https://via.placeholder.com/150', 3, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (102, '9787208171336', '置身事内', '兰小欢', '中国政府在经济发展中的作用。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (103, '9787100029320', '国富论', '亚当·斯密', '经济学鼻祖亚当·斯密的传世经典。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (104, '9787301256619', '经济学原理', '曼昆', '最受欢迎的经济学入门教材。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (105, '9787010041445', '资本论', '马克思', '马克思主义政治经济学的奠基之作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (106, '9787100021676', '就业、利息和货币通论', '凯恩斯', '宏观经济学的奠基之作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (107, '9787508633558', '思考，快与慢', '丹尼尔·卡尼曼', '诺贝尔经济学奖得主的心理学杰作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (108, '9787508616483', '穷查理宝典', '查理·芒格', '巴菲特黄金搭档查理·芒格的智慧箴言录。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (109, '9787508684031', '原则', '瑞·达利欧', '桥水基金创始人瑞·达利欧的人生和工作原则。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (110, '9787111267652', '卓有成效的管理者', '彼得·德鲁克', '管理学之父德鲁克的成名作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (111, '9787508616513', '基业长青', '吉姆·柯林斯', '通过对18家高瞻远瞩公司的研究，揭示了企业永续经营的准则。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (112, '9787508616520', '从优秀到卓越', '吉姆·柯林斯', '柯林斯“基业长青”三部曲之二。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (113, '9787508616537', '创新者的窘境', '克莱顿·克里斯坦森', '管理大师克里斯坦森的经典之作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (114, '9787508616544', '黑天鹅', '纳西姆·尼古拉斯·塔勒布', '如何应对不可预知的未来。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (115, '9787508616551', '反脆弱', '纳西姆·尼古拉斯·塔勒布', '从不确定性中获益。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (116, '9787508616568', '随机漫步的傻瓜', '纳西姆·尼古拉斯·塔勒布', '发现市场和人生中的运气成分。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (117, '9787508616575', '赢', '杰克·韦尔奇', '通用电气前CEO杰克·韦尔奇的管理心得。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (118, '9787508616582', '只有偏执狂才能生存', '安迪·格鲁夫', '英特尔前CEO安迪·格鲁夫的自传。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (119, '9787508630069', '乔布斯传', '沃尔特·艾萨克森', '乔布斯唯一授权的官方传记。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (120, '9787550284463', '鞋狗', '菲尔·奈特', '耐克创始人菲尔·奈特的亲笔自传。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (121, '9787508643328', '一网打尽', '布拉德·斯通', '贝佐斯与亚马逊时代。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (122, '9787550290594', '腾讯传', '吴晓波', '全景式记录腾讯崛起的历程。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (123, '9787508658827', '阿里巴巴：马云的商业帝国', '克拉克', '深入揭秘阿里巴巴的成长史。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (124, '9787508608679', '货币战争', '宋鸿兵', '揭示了货币背后的惊天阴谋。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (125, '9787508620787', '富爸爸穷爸爸', '罗伯特·清崎', '财商教育的经典之作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (126, '9787536551817', '小狗钱钱', '博多·舍费尔', '理财入门的童话故事。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (127, '9787300073231', '影响力', '罗伯特·西奥迪尼', '解释了为什么顺从别人会成为一种习惯。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (128, '9787500660651', '乌合之众', '古斯塔夫·勒庞', '群体心理学的开山之作。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (129, '9787300038933', '非理性繁荣', '罗伯特·席勒', '对股市泡沫的深入分析。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (130, '9787508626604', '大空头', '迈克尔·刘易斯', '记录了2008年金融危机中的做空者。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (131, '9787508626086', '伟大的博弈', '约翰·斯蒂尔·戈登', '华尔街的历史。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (132, '9787508682853', '激荡十年', '吴晓波', '水大鱼大。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (133, '9787540462782', '历代经济变革得失', '吴晓波', '梳理了中国历史上的经济变革。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (134, '9787544710882', '我们时代的神经症', '卡伦·霍妮', '对现代人心理问题的深入剖析。', 'https://via.placeholder.com/150', 4, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (135, '9787111495482', '被讨厌的勇气', '岸见一郎', '“自我启发之父”阿德勒的哲学课。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (136, '9787100015507', '梦的解析', '西格蒙德·弗洛伊德', '精神分析学派的奠基之作。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (137, '9787508639536', '自卑与超越', '阿尔弗雷德·阿德勒', '阿德勒个体心理学的代表作。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (138, '9787544710325', '荣格自传', '卡尔·荣格', '分析心理学创始人荣格的自传。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (139, '9787115147820', '社会心理学', '戴维·迈尔斯', '被美国700多所大学选为教材。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (140, '9787115111302', '心理学与生活', '理查德·格里格', '心理学入门的经典教材。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (141, '9787300092928', '津巴多普通心理学', '菲利普·津巴多', '当代心理学大师津巴多的代表作。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (142, '9787201052601', '少有人走的路', 'M·斯科特·派克', '心智成熟的旅程。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (143, '9787508051284', '非暴力沟通', '马歇尔·卢森堡', '一种沟通方式，一种生活态度。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (144, '9787115243881', '亲密关系', '罗兰·米勒', '两性关系的百科全书。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (145, '9787532744572', '爱的艺术', '埃里希·弗洛姆', '爱是一种能力，需要学习和练习。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (146, '9787532744565', '逃避自由', '埃里希·弗洛姆', '探讨了现代人逃避自由的心理机制。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (147, '9787500660651', '乌合之众', '古斯塔夫·勒庞', '群体心理学的开山之作。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (148, '9787563391807', '狂热分子', '埃里克·霍弗', '码头工人哲学家对群众运动的思考。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (149, '9787108033626', '路西法效应', '菲利普·津巴多', '好人是如何变成恶魔的。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (150, '9787300073231', '影响力', '罗伯特·西奥迪尼', '解释了为什么顺从别人会成为一种习惯。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (151, '9787213077181', '先发影响力', '罗伯特·西奥迪尼', '如何在别人开口之前就影响他。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (152, '9787508633558', '思考，快与慢', '丹尼尔·卡尼曼', '诺贝尔经济学奖得主的心理学杰作。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (153, '9787508616599', '怪诞行为学', '丹·艾瑞里', '可预测的非理性。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (154, '9787508616605', '助推', '理查德·泰勒', '如何做出更好的选择。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (155, '9787508682877', '心流', '米哈里·契克森米哈赖', '最优体验心理学。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (156, '9787508622620', '积极心理学', '马丁·塞利格曼', '幸福的科学。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (157, '9787508621425', '活出意义来', '维克多·弗兰克', '在纳粹集中营中寻找生命的意义。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (158, '9787544710875', '我们内心的冲突', '卡伦·霍妮', '对现代人内心冲突的深入剖析。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (159, '9787115220479', '改变心理学的40项研究', '罗杰·霍克', '探索心理学历史上的经典实验。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (160, '9787115269478', '对伪心理学说不', '基思·斯坦诺维奇', '像心理学家一样思考。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (161, '9787100054773', '进化心理学', '大卫·巴斯', '心理的新科学。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (162, '9787301099681', '认知心理学', '罗伯特·索尔索', '探索人类心智的奥秘。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (163, '9787506292351', '发展心理学', '费尔德曼', '人的毕生发展。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (164, '9787115183309', '变态心理学', '苏珊·诺伦-霍克西玛', '探索心理异常的奥秘。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (165, '9787501974757', '人格心理学', 'Jerry M. Burger', '经典的人格心理学教材。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (166, '9787201161693', '蛤蟆先生去看心理医生', '罗伯特·戴博德', '讲述了蛤蟆先生在心理咨询中的成长故事。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (167, '9787544280590', '也许你该找个人聊聊', '洛莉·戈特利布', '一位心理治疗师的回忆录。', 'https://via.placeholder.com/150', 5, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (168, '9787544246183', '白夜行', '东野圭吾', '只希望能手牵手在太阳下散步。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (169, '9787544241690', '嫌疑人X的献身', '东野圭吾', '究竟爱一个人，可以爱到什么地步？', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (170, '9787544270874', '解忧杂货店', '东野圭吾', '现代人内心流失的东西，这家杂货店能帮你找回。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (171, '9787544244127', '恶意', '东野圭吾', '无边的恶意，深不见底。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (172, '9787544245612', '放学后', '东野圭吾', '东野圭吾的成名作，获江户川乱步奖。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (173, '9787544241478', '秘密', '东野圭吾', '获日本推理作家协会奖。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (174, '9787544255178', '新参者', '东野圭吾', '加贺恭一郎系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (175, '9787544255185', '红手指', '东野圭吾', '加贺恭一郎系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (176, '9787544255192', '麒麟之翼', '东野圭吾', '加贺恭一郎系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (177, '9787500115588', '福尔摩斯探案全集', '柯南·道尔', '侦探小说的鼻祖。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (178, '9787513322881', '无人生还', '阿加莎·克里斯蒂', '孤岛模式的开山之作。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (179, '9787513322898', '东方快车谋杀案', '阿加莎·克里斯蒂', '波洛侦探系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (180, '9787513322904', '尼罗河上的惨案', '阿加莎·克里斯蒂', '波洛侦探系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (181, '9787513322911', '罗杰疑案', '阿加莎·克里斯蒂', '阿加莎的成名作。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (182, '9787513322928', 'ABC谋杀案', '阿加莎·克里斯蒂', '波洛侦探系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (183, '9787020049295', '达·芬奇密码', '丹·布朗', '兰登教授系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (184, '9787020054046', '天使与魔鬼', '丹·布朗', '兰登教授系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (185, '9787020077861', '失落的秘符', '丹·布朗', '兰登教授系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (186, '9787020101740', '地狱', '丹·布朗', '兰登教授系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (187, '9787020138678', '本源', '丹·布朗', '兰登教授系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (188, '9787544733904', '沉默的羔羊', '托马斯·哈里斯', '汉尼拔系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (189, '9787544733911', '红龙', '托马斯·哈里斯', '汉尼拔系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (190, '9787544733928', '汉尼拔', '托马斯·哈里斯', '汉尼拔系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (191, '9787544266396', '教父', '马里奥·普佐', '黑帮小说的巅峰之作。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (192, '9787544237099', '漫长的告别', '雷蒙德·钱德勒', '硬汉派侦探小说的代表作。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (193, '9787540478790', '长夜难明', '紫金陈', '为了查清真相，检察官付出了生命的代价。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (194, '9787540462690', '坏小孩', '紫金陈', '隐秘的角落原著。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (195, '9787540462706', '无证之罪', '紫金陈', '社会派推理小说。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (196, '9787229002238', '心理罪', '雷米', '方木系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (197, '9787540457597', '法医秦明', '秦明', '万象卷。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (198, '9787540457603', '尸语者', '秦明', '法医秦明系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (199, '9787540457610', '无声的证词', '秦明', '法医秦明系列。', 'https://via.placeholder.com/150', 6, 0);
INSERT INTO `books` (`id`, `isbn`, `title`, `author`, `description`, `cover_url`, `category_id`, `average_rating`) VALUES (200, '9787540457627', '第十一根手指', '秦明', '法医秦明系列。', 'https://via.placeholder.com/150', 6, 0);

-- Insert Interactions (Mock History)
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (1, 1, 1, 'click');
INSERT INTO `ratings` (`id`, `user_id`, `book_id`, `rating`) VALUES (1, 1, 1, 5);
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (2, 1, 2, 'click');
INSERT INTO `ratings` (`id`, `user_id`, `book_id`, `rating`) VALUES (2, 1, 2, 5);
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (3, 1, 3, 'click');
INSERT INTO `ratings` (`id`, `user_id`, `book_id`, `rating`) VALUES (3, 1, 3, 5);
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (4, 1, 4, 'click');
INSERT INTO `ratings` (`id`, `user_id`, `book_id`, `rating`) VALUES (4, 1, 4, 5);
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (5, 1, 5, 'click');
INSERT INTO `ratings` (`id`, `user_id`, `book_id`, `rating`) VALUES (5, 1, 5, 5);
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (6, 2, 36, 'collect');
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (7, 2, 37, 'collect');
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (8, 2, 38, 'collect');
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (9, 2, 39, 'collect');
INSERT INTO `interactions` (`id`, `user_id`, `book_id`, `interaction_type`) VALUES (10, 2, 40, 'collect');

SET FOREIGN_KEY_CHECKS = 1;