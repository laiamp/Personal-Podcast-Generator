<script lang="ts">
  export let durationMins = 15;
  export let voice = 'conversational';
  export let selectedTopics: string[] = [];
  export let isGenerating = false;
  export let statusMessage = '';
  export let errorMessage = '';
  export let onGenerate: () => void = () => {};

  const durationOptions = [5, 10, 15, 20, 25, 30];

  const voiceOptions = [
    { value: 'conversational', label: 'Conversational Friendly', description: 'Warm, paced, and easy to follow.' },
    { value: 'newsroom', label: 'Professional News Anchored', description: 'Clear, concise, and editorial.' },
    { value: 'minimalist', label: 'Just the Facts, Quick', description: 'Tight delivery with low friction.' },
  ];

  const topicOptions = [
    { label: 'Tech & AI', badge: '🤖', description: 'Silicon Valley breakthroughs and software news' },
    { label: 'Global Finance', badge: '📈', description: 'Market movements and macroeconomic updates' },
    { label: 'Daily Brief', badge: '📰', description: 'General world news headlines and weather' },
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
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Generate Podcast</p>
      <h2 class="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Control Center</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
        Tune the briefing before the generator starts. Once the briefing is ready, this entire selector fades out.
      </p>
    </div>
 
  </div>

  <div class="mt-8 grid gap-4 lg:grid-cols-[1.2fr_0.9fr_1fr]">
    <section class="rounded-[1.5rem] border border-slate-200 bg-slate-50/80 p-4">
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Topics</h3>
        <span class="text-xs text-slate-500">Choose one or more</span>
      </div>

      <div class="mt-4 space-y-3">
        {#each topicOptions as topic}
          <label class:selected={selectedTopics.includes(topic.label)} class="group flex cursor-pointer items-start gap-3 rounded-2xl border border-slate-200 bg-white p-3 transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-sm">
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
              <small class="mt-1 block text-sm leading-5 text-slate-500">{topic.description}</small>
            </span>
          </label>
        {/each}
      </div>
    </section>

    <section class="rounded-[1.5rem] border border-slate-200 bg-white p-4">
      <div class="flex items-center justify-between gap-3">
        <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Commute Budget</h3>
        <span class="text-xs text-slate-500">{durationMins} min</span>
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

        <div class="mt-3 flex justify-between text-[0.7rem] font-medium uppercase tracking-[0.16em] text-slate-400">
          {#each durationOptions as option}
            <span>{option}m</span>
          {/each}
        </div>
      </div>

      <div class="mt-6">
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Voice Delivery</h3>
          <span class="text-xs text-slate-500">{selectedVoiceLabel}</span>
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

        <p class="mt-3 text-sm leading-6 text-slate-500">
          {voiceOptions.find((option) => option.value === voice)?.description}
        </p>
      </div>
    </section>

    <section class="flex flex-col rounded-[1.5rem] border border-slate-200 bg-slate-950 p-4 text-white shadow-inner shadow-slate-950/20">
      <button
        class="mt-6 inline-flex items-center justify-center rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
        on:click={onGenerate}
        disabled={isGenerating || selectedTopics.length === 0}
      >
        {isGenerating ? 'Generating Morning Podcast...' : 'Generate Morning Podcast'}
      </button>

      <p class="mt-4 text-sm leading-6 {errorMessage ? 'text-rose-300' : 'text-slate-300'}">
        {errorMessage || statusMessage}
      </p>
    </section>
  </div>
</section>
