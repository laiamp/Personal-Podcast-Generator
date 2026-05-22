<script lang="ts">
  import { onDestroy } from 'svelte';
  import PreferenceSelector from '../../lib/components/PreferenceSelector.svelte';
  import GenerationLoader from '../../lib/components/GenerationLoader.svelte';
  import BriefingPlayer from '../../lib/components/BriefingPlayer.svelte';
  const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

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
    statusMessage = 'Requesting generation...';

    (async () => {
      try {
        const payload = {
          user_id: 'test-user',
          interests_query: selectedTopics.join(', '),
          voice_type: voice,
          source_limit: 5,
        };

        statusMessage = 'Sending request to generator...';
        const resp = await fetch(`${API_BASE}/podcasts/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        let responseData = null;
        if (!resp.ok) {
          // Try to parse JSON error body, otherwise fall back to text
          let errBody = null;
          try {
            errBody = await resp.json();
          } catch (_) {
            try {
              errBody = await resp.text();
            } catch (_) {
              errBody = null;
            }
          }

          const detailText = errBody && typeof errBody === 'object' ? errBody.detail || JSON.stringify(errBody) : String(errBody || `Server returned ${resp.status}`);

          // If the backend reports no sources for the filtered query, retry without a query
          if (resp.status === 400 && String(detailText).includes('No sources available')) {
            statusMessage = 'No matching sources found — retrying with broader source set...';
            const retryPayload = { ...payload, interests_query: null };
            const retryResp = await fetch(`${API_BASE}/podcasts/generate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(retryPayload),
            });

            if (!retryResp.ok) {
              let retryErrBody = null;
              try { retryErrBody = await retryResp.json(); } catch (_) { retryErrBody = await retryResp.text().catch(() => null); }
              const retryDetail = retryErrBody && typeof retryErrBody === 'object' ? retryErrBody.detail || JSON.stringify(retryErrBody) : String(retryErrBody || `Server returned ${retryResp.status}`);
              throw new Error(retryDetail);
            }

            responseData = await retryResp.json().catch(() => ({}));
          } else {
            throw new Error(detailText);
          }
        } else {
          responseData = await resp.json().catch(() => ({}));
        }

        const data = responseData || {};
        const podcast = data.podcast;
        let audioUrl = podcast.audio_url || podcast.audioUrl || '';

        const resolvedAudioUrl = audioUrl.startsWith('http') ? audioUrl : new URL(audioUrl, API_BASE).toString();

        generatedEpisode = {
          id: podcast._id || podcast.id || `generated-${Date.now()}`,
          title: podcast.title || `Custom Briefing: ${selectedTopics.join(', ')}`,
          createdAt: podcast.created_at || new Date().toISOString(),
          topics: [...selectedTopics],
          durationMins: Math.round((podcast.duration_seconds || 60) / 60),
          voice,
          summary: podcast.script || podcast.summary || '',
          audioUrl: resolvedAudioUrl,
        };

        generationStage = 'loaded';
        statusMessage = 'Your briefing is ready.';
      } catch (err) {
        console.error(err);
        errorMessage = err instanceof Error ? err.message : String(err || 'Generation failed');
        generationStage = 'idle';
      } finally {
        isGenerating = false;
      }
    })();
  }

  onDestroy(clearPendingTimers);
</script>

<svelte:head>
  <title>Generate</title>
</svelte:head>

<main class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
  <section class="mx-auto flex w-full max-w-6xl flex-col gap-6">
   

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
