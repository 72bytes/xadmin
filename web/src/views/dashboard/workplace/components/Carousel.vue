<template>
  <a-carousel
    indicator-type="slider"
    show-arrow="hover"
    auto-play
    style="width: 100%; height: 150px; border-radius: 4px; overflow: hidden"
  >
    <a-carousel-item v-for="(image, idx) in images" :key="idx">
      <div>
        <a-link
          :href="image.url"
          target="_blank"
          rel="noopener"
        >
          <img :src="image.src" style="width: 100%" alt="" />
        </a-link>
      </div>
    </a-carousel-item>
  </a-carousel>
</template>

<script setup lang="ts">
const images = [
  {
    src: `https://continew.top/qrcode-text.jpg?${new Date().getTime()}`,
    url: 'https://continew.top/about/intro.html',
  },
  {
    src: `https://continew.top/sponsor.jpg?${new Date().getTime()}`,
    url: 'https://continew.top/sponsor.html',
  },
]
</script>
