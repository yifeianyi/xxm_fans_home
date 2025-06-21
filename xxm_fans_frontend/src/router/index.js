import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import SongList from '../views/SongList.vue'
import TopChart from '../views/TopChart.vue'

const routes = [
    {
        path: '/',
        redirect: '/songs'//默认跳转到歌单页
    },
    {
        path: '/songs',
        name: 'SongList',
        component: SongList
    },
    {
        path: '/top',
        name: "TopChart",
        component: TopChart
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router