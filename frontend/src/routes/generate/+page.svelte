<script lang="ts">
  import { onDestroy } from 'svelte';
  import PreferenceSelector from '../../lib/components/PreferenceSelector.svelte';
  import GenerationLoader from '../../lib/components/GenerationLoader.svelte';
  import BriefingPlayer from '../../lib/components/BriefingPlayer.svelte';

  interface BriefingEpisode {
    id: string;
    title: string;
    createdAt: string;
    topics: string[];
    durationMins: number;
    voice: string;
    summary: string;
    audioUrl: string;
  }

  type GenerationStage = 'idle' | 'loading' | 'loaded';

  const mockAudioUrl = createSilentWavUrl(6);

  let generationStage: GenerationStage = 'idle';
  let isGenerating = false;
  let statusMessage = 'Ready to compile your daily update.';
  let errorMessage = '';

  let durationMins = 15;
  let voice = 'conversational';
  let selectedTopics: string[] = [];

  const voiceOptions = [
    { value: 'conversational', label: 'Conversational Friendly' },
    { value: 'newsroom', label: 'Professional News Anchored' },
    { value: 'minimalist', label: 'Just the Facts, Quick' },
  ];

  let generatedEpisode: BriefingEpisode = {
    id: 'generated-preview',
    title: 'Your custom briefing will appear here',
    createdAt: new Date().toISOString(),
    topics: [],
    durationMins,
    voice,
    summary: 'Pick a few topics, generate the briefing, and the player will replace the selector.',
    audioUrl: mockAudioUrl,
  };

  let loadingTimers: ReturnType<typeof setTimeout>[] = [];

  $: selectedVoiceLabel = voiceOptions.find((option) => option.value === voice)?.label ?? voice;

  function createSilentWavUrl(_seconds: number): string {
    return 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==';
  }

  function clearPendingTimers() {
    for (const timer of loadingTimers) {
      clearTimeout(timer);
    }

    loadingTimers = [];
  }

  function buildGeneratedEpisode(): BriefingEpisode {
    const topicLine = selectedTopics.length > 0 ? selectedTopics.join(', ') : 'Curated headlines';

    return {
      id: `generated-${Date.now()}`,
      title: `Custom Briefing: ${topicLine}`,
      createdAt: new Date().toISOString(),
      topics: [...selectedTopics],
      durationMins,
      voice,
      summary: `A ${durationMins}-minute briefing shaped around ${topicLine.toLowerCase()} and delivered in a ${selectedVoiceLabel.toLowerCase()} style.`,
      audioUrl: mockAudioUrl,
    };
  }

  function generatePodcast() {
    if (selectedTopics.length === 0) {
      errorMessage = 'Select at least one topic before generating.';
      return;
    }

    clearPendingTimers();
    isGenerating = true;
    errorMessage = '';
    generationStage = 'loading';
    statusMessage = 'Gathering morning headers...';

    loadingTimers.push(
      setTimeout(() => {
        statusMessage = 'Synthesizing the final script...';
      }, 1200),
    );

    loadingTimers.push(
      setTimeout(() => {
        generatedEpisode = buildGeneratedEpisode();
        generationStage = 'loaded';
        isGenerating = false;
        statusMessage = 'Your briefing is ready.';
      }, 2500),
    );
  }

  onDestroy(clearPendingTimers);
</script>

<svelte:head>
  <title>Generate</title>
</svelte:head>

<main class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
  <section class="mx-auto flex w-full max-w-6xl flex-col gap-6">
    <div class="flex items-center justify-between gap-4 px-1 text-sm text-slate-500">
      <div>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Custom AI Podcast Generator</p>
        <p class="mt-1 text-sm text-slate-500">Fine-tune the setup, wait for curation, then drop straight into the player.</p>
      </div>
      <span class="hidden rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-xs font-medium text-slate-500 shadow-sm sm:inline-flex">{generationStage}</span>
    </div>

    {#if generationStage === 'idle'}
      <PreferenceSelector
        bind:durationMins
        bind:voice
        bind:selectedTopics
        {statusMessage}
        {errorMessage}
        {isGenerating}
        onGenerate={generatePodcast}
      />
    {:else if generationStage === 'loading'}
      <GenerationLoader {statusMessage} />
    {:else}
      <BriefingPlayer episode={generatedEpisode} />
    {/if}
  </section>
</main>
