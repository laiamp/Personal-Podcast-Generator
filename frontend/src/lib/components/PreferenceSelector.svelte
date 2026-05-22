<script lang="ts">
  export let durationMins = 15;
  export let voice = 'conversational';
  export let selectedTopics: string[] = [];
  export let isGenerating = false;
  export let statusMessage = '';
  export let errorMessage = '';
  export let onGenerate: () => void = () => {};

  const durationOptions = [1, 5, 10, 15, 20];

  const voiceOptions = [
    { value: 'conversational', label: 'Conversational Friendly', description: 'Warm, paced, and easy to follow.' },
    { value: 'newsroom', label: 'Professional News Anchored', description: 'Clear, concise, and editorial.' },
    { value: 'minimalist', label: 'Just the Facts, Quick', description: 'Tight delivery with low friction.' },
  ];

  const topicOptions = [
    { label: 'Frontier Labs', badge: '🧠', description: 'LLMs, autonomous agents, and breakthrough research from major AI labs' },
    { label: 'Startups and Venture', badge: '🚀', description: 'Venture capital rounds, founder stories, and tech market shifts' },
    { label: 'Geopolitics', badge: '🌍', description: 'Global political developments and their impact on technology and society' },
    { label: 'Tech and Tools', badge: '💻', description: 'Latest technological advancements and useful tools for professionals' },
  ];

  $: selectedVoiceLabel = voiceOptions.find((option) => option.value === voice)?.label ?? voice;
  $: topicSummary = selectedTopics.length > 0 ? selectedTopics.join(', ') : 'No topics selected';

  function toggleTopic(topicLabel: string) {
    if (selectedTopics.includes(topicLabel)) {
      selectedTopics = selectedTopics.filter((topic) => topic !== topicLabel);
      return;
    }

    selectedTopics = [...selectedTopics, topicLabel];
  }
</script>

<section class="relative overflow-hidden rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_32px_80px_rgba(15,23,42,0.08)] backdrop-blur">
  <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-300 to-transparent"></div>

  <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
    <div>
      <h2 class="mt-2 text-center text-3xl font-semibold tracking-tight text-slate-950">Generate Podcast</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-700">
        Tune the briefing before the generator starts. Once the briefing is ready, this entire selector fades out.
      </p>
    </div>
 
  </div>

  <div class="mt-8 grid gap-4 lg:grid-cols-[1.2fr_0.9fr_1fr]">
    <section class="rounded-[1.5rem] border border-slate-200 bg-slate-50/80 p-4">
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Topics</h3>
        <span class="text-xs text-slate-600">Choose one or more</span>
      </div>

      <div class="mt-4 space-y-3">
        {#each topicOptions as topic}
          <label class:selected={selectedTopics.includes(topic.label)} class="group flex cursor-pointer items-start gap-3 rounded-2xl border border-slate-300 bg-white p-3 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-500 hover:bg-slate-50 hover:shadow">
            <input
              type="checkbox"
              class="mt-1 h-4 w-4 rounded border-slate-300 text-slate-950"
              checked={selectedTopics.includes(topic.label)}
              on:change={() => toggleTopic(topic.label)}
            />

            <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-slate-100 text-lg">
              {topic.badge}
            </span>

            <span class="min-w-0">
              <strong class="block text-sm font-semibold text-slate-950">{topic.label}</strong>
              <small class="mt-1 block text-sm leading-5 text-slate-700">{topic.description}</small>
            </span>
          </label>
        {/each}
      </div>
    </section>

    <section class="rounded-[1.5rem] border border-slate-200 bg-white p-4">
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Commute Budget</h3>
        <span class="text-xs font-medium text-slate-700">{durationMins} min</span>
      </div>

      <div class="mt-5">
        <input
          type="range"
          min={durationOptions[0]}
          max={durationOptions[durationOptions.length - 1]}
          step="5"
          bind:value={durationMins}
          aria-label="Commute Time Budget"
          class="range-slider w-full"
        />

        <div class="mt-3 flex justify-between text-[0.7rem] font-medium uppercase tracking-[0.16em] text-slate-500">
          {#each durationOptions as option}
            <span>{option}m</span>
          {/each}
        </div>
      </div>

      <div class="mt-6">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Voice Delivery</h3>
        </div>

        <select
          bind:value={voice}
          aria-label="Voice Type"
          class="mt-4 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-900 outline-none transition focus:border-slate-400"
        >
          {#each voiceOptions as option}
            <option value={option.value}>{option.label}</option>
          {/each}
        </select>

        <p class="mt-3 text-sm leading-6 text-slate-700">
          {voiceOptions.find((option) => option.value === voice)?.description}
        </p>
      </div>
    </section>

    <section class="flex flex-col rounded-[1.5rem] border border-slate-200 bg-slate-950 p-4 text-white shadow-inner shadow-slate-950/20">
      <button
        class="mt-6 inline-flex items-center justify-center rounded-2xl border border-slate-100 bg-white px-4 py-3 text-sm font-bold text-slate-950 shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 disabled:cursor-not-allowed disabled:border-slate-300 disabled:bg-slate-300 disabled:text-slate-700 disabled:opacity-100"
        on:click={onGenerate}
        disabled={isGenerating || selectedTopics.length === 0}
      >
        {isGenerating ? 'Generating Morning Podcast...' : 'Generate Morning Podcast'}
      </button>

      <p class="mt-4 text-sm leading-6 {errorMessage ? 'text-rose-200' : 'text-slate-100'}">
        {errorMessage || statusMessage}
      </p>
    </section>
  </div>
</section>

<style>
  label.selected {
    border-color: rgb(51 65 85 / 0.55);
    background: rgb(241 245 249);
  }

  label.selected strong {
    color: rgb(15 23 42);
  }
</style>
