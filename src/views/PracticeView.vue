<script setup>
import SampleOne from '../components/SampleOne.vue'
import SampleTwo from '../components/SampleTwo.vue'
import VHtml from '../components/v-html.vue'
import Xss from '../components/XSS.vue'
import VText from '../components/v-text.vue'
import VBind from '../components/v-bind.vue'
import ClassBinding from '../components/ClassBinding.vue'
import StyleBinding from '../components/StyleBinding.vue'
import VCondition from '../components/VCondition.vue'
import VShow from '../components/v-show.vue'
import VFor from '../components/v-for.vue'
import VPre from '../components/v-pre.vue'
import VOn from '../components/v-on.vue'
import EventObject from '@/components/event-object.vue'
import EventModifier from '@/components/event-modifier.vue'
import VModelForm from '@/components/VModelForm.vue'
import VModelModifiers from '@/components/VModelModifiers.vue'
import LifecycleHook from '@/components/LifecycleHook.vue'
import SlotDefaultParent from '@/components/SlotDefaultParent.vue'
import SlotNameParent from '@/components/SlotNameParent.vue'
</script>
<template>
  <main class="container">
    <SampleOne />
    <SampleTwo />
    <v-html />
    <Xss />
    <VText />
    <VBind />
    <RouterView />
    <ClassBinding />
    <StyleBinding />
    <VCondition />
    <VShow />
    <VFor />
    <VPre />
    <VOn />
    <EventObject />
    <EventModifier />
    <VModelForm />
    <VModelModifiers />
    <LifecycleHook />
    <SlotDefaultParent />
    <SlotNameParent />
  </main>
</template>

<style scoped>
.container {
  max-width: 768px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.container > * {
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.container > * + * {
  border-top: 1px solid #e2e8f0;
  padding-top: 2rem;
}
</style>
