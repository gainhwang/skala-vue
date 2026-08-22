import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/views/final/FinalLayoutView.vue'),
      meta: {
        standalone: true,
      },
      children: [
        {
          path: '',
          name: 'weather-final',
          component: () => import('@/views/final/TodayGamesView.vue'),
        },
        {
          path: 'game/:gameId',
          name: 'final-game-detail',
          component: () => import('@/views/final/GameDetailView.vue'),
          props: true,
        },
        {
          path: 'stadiums',
          name: 'final-stadiums',
          component: () => import('@/views/final/StadiumGuideView.vue'),
        },
        {
          path: 'favorite',
          name: 'final-favorite',
          component: () => import('@/views/final/FavoriteTeamView.vue'),
        },
      ],
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/practice',
      name: 'practice',
      component: () => import('../views/PracticeView.vue'),
    },
    {
      path: '/exercise',
      name: 'exercise',
      component: () => import('../views/ExerciseLayoutView.vue'),
      redirect: { name: 'exercise-mockup' },
      children: [
        {
          path: 'mockup',
          name: 'exercise-mockup',
          component: () => import('@/views/exercise/MockupView.vue'),
        },
        {
          path: 'composition',
          name: 'exercise-composition',
          component: () => import('@/views/exercise/CompositionView.vue'),
        },
        {
          path: 'component',
          name: 'exercise-components',
          component: () => import('@/views/exercise/ComponentsView.vue'),
        },
        {
          path: 'router',
          name: 'exercise-router',
          component: () => import('@/views/exercise/router/RouterLayoutView.vue'),
          children: [
            {
              path: '',
              name: 'exercise-router-home',
              component: () => import('@/views/exercise/router/RouterHomeView.vue'),
            },
            {
              path: 'about',
              name: 'exercise-router-about',
              component: () => import('@/views/exercise/router/RouterAboutView.vue'),
            },
            {
              path: 'weather/:cityId',
              name: 'exercise-weather-detail',
              component: () => import('@/views/exercise/router/WeatherDetailView.vue'),
              props: true,
            },
            {
              path: ':pathMatch(.*)*',
              name: 'exercise-router-not-found',
              component: () => import('@/views/exercise/router/RouterNotFoundView.vue'),
            },
          ],
        },
        {
          path: 'store',
          name: 'exercise-store',
          component: () => import('@/views/exercise/store/WeatherStoreView.vue'),
        },
        {
          path: 'store/weather/:cityId',
          name: 'exercise-store-detail',
          component: () => import('@/views/exercise/store/StoreDetailView.vue'),
          props: true,
        },
        {
          path: 'axios',
          name: 'exercise-axios',
          component: () => import('@/views/exercise/axios/WeatherAxiosView.vue'),
        },
      ],
    },
  ],
})

export default router
