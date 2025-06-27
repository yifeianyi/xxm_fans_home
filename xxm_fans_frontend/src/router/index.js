import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import SongTabs from '../components/SongTabs.vue'
import Footprint from '../views/Footprint.vue'

const routes = [
    {
        path: '/',
        redirect: '/songs'//默认跳转到歌单页
    },
    {
        path: '/songs',
        name: 'SongTabs',
        component: SongTabs
    },
    {
        path: '/footprint',
        name: 'Footprint',
        component: Footprint
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router