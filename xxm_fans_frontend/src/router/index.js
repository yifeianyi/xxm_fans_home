import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import SongTabs from '../views/SongTabs.vue'

const routes = [
    {
        path: '/',
        redirect: '/songs'//默认跳转到歌单页

    },
    {
        path: '/songs',
        name: 'SongTabs',
        component: SongTabs
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router