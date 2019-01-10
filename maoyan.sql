/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 100119
 Source Host           : localhost:3306
 Source Schema         : maoyan

 Target Server Type    : MySQL
 Target Server Version : 100119
 File Encoding         : 65001

 Date: 10/01/2019 19:09:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for comments
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '来源id',
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '内容',
  `nick` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '昵称',
  `score` decimal(11, 2) NOT NULL COMMENT '评分',
  `time` int(11) NOT NULL COMMENT '发布时间',
  `create_at` int(11) NOT NULL COMMENT '创建时间',
  `movie_id` int(11) NOT NULL COMMENT '电影id',
  `gender` tinyint(1) NOT NULL COMMENT '1男0女',
  `city` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '城市名称',
  `buytick` tinyint(1) NULL DEFAULT 0 COMMENT '是否购票',
  `userlevel` int(11) NULL DEFAULT 0 COMMENT '用户等级',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '用户头像',
  `approve` int(11) NULL DEFAULT 0 COMMENT '点赞数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 121262 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for movies
-- ----------------------------
DROP TABLE IF EXISTS `movies`;
CREATE TABLE `movies`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `en_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '英文名',
  `ch_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '中文名',
  `source_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '来源id',
  `zone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '区域',
  `cat` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '分类',
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '描述',
  `star` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '演员',
  `director` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '导演',
  `score` decimal(11, 2) NOT NULL COMMENT '评分',
  `cover` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '封面',
  `score_num` int(11) NOT NULL COMMENT '评分人数',
  `lang` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '语言',
  `release_date` date NOT NULL COMMENT '发布日期',
  `create_at` int(11) NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
