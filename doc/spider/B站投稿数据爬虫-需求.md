# B站投稿数据定时捕获爬虫

1. 导出 data_analytics_workstatic 中的数据保存为data/spider/views.json
   1. 每次 data_analytics_workstatic  表有数据更新时，自动更新views.json文件
2. 爬虫根据 views.json 中 的is_valid 字段是否爬取该B站视频
   1. 爬取的信息包括：播放数、弹幕数、评论数、点赞数、投币数、收藏数、转发数
3. 每次爬回来获取到的信息保存到data/spider/views/{year}/{month}/{day}/{year}-{month}-{day}-{hour}_views_data.json下
4. 每次爬取结束后，自动把data/spider/views/{year}/{month}/{day}/{year}-{month}-{day}-{hour}_views_data.json 中的所有具体投稿数据导入到data/view_data.sqlite3下
5. 爬取过程中需要记录日志信息，日志文件保存到 logs/spider 下
6. 爬虫需要有完备的异常处理机制
7. 爬虫的主控脚本放到spider下，其它部分放到后端目录的tools/spider下
8. 两个投稿的数据爬取间隔需要在0.2-0.5s间（随机间隔） 