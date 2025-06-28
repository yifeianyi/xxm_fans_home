import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import SongTabs from '../components/SongTabs.vue'
import Footprint from '../views/Footprint.vue'
import MobileHello from '../views/MobileHello.vue'

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
    }//,
    // {
    //     path: '/mobile-hello',
    //     name: 'MobileHello',
    //     component: MobileHello
    // }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// router.beforeEach(async (to, from, next) => {
//     if (to.path === '/songs') {
//         try {
//             const res = await fetch('/api/is_mobile/')
//             const data = await res.json()
//             if (data.is_mobile) {
//                 next('/mobile-hello')
//                 return
//             }
//         } catch (e) { }
//     }
//     next()
// })

export default router