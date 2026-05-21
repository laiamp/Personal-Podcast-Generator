<script lang="ts">
  import { goto } from '$app/navigation';

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

  export let episode: BriefingEpisode;
  export let historyHref = '/history';
  export let adminHref = '/kpis';

  let audioElement: HTMLAudioElement | null = null;
  let isPaused = true;
  let currentTime = 0;
  let duration = 0;
  let statusMessage = 'Ready to play.';
  let errorMessage = '';

  $: if (episode) {
    isPaused = true;
    currentTime = 0;
    duration = 0;
    statusMessage = `Loaded: ${episode.title}`;
    errorMessage = '';
  }

  $: progress = duration > 0 ? Math.min((currentTime / duration) * 100, 100) : 0;

  function formatTime(seconds: number): string {
    if (!Number.isFinite(seconds) || seconds < 0) return '0:00';

    const wholeSeconds = Math.floor(seconds);
    const minutes = Math.floor(wholeSeconds / 60);
    const remainingSeconds = wholeSeconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  function togglePlayback() {
    if (!audioElement) return;

    if (isPaused) {
      audioElement
        .play()
        .then(() => {
          statusMessage = 'Playing briefing.';
        })
        .catch(() => {
          errorMessage = 'Playback is blocked. Use the browser controls if needed.';
        });
      return;
    }

    audioElement.pause();
    statusMessage = 'Paused.';
  }

  function rewind() {
    if (!audioElement) return;
    audioElement.currentTime = Math.max(audioElement.currentTime - 15, 0);
  }

  function fastForward() {
    if (!audioElement) return;
    audioElement.currentTime = Math.min(audioElement.currentTime + 15, duration || audioElement.currentTime + 15);
  }

  function openHistory() {
    goto(historyHref);
  }

  function openAdmin() {
    goto(adminHref);
  }
</script>

<section class="relative overflow-hidden rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_32px_80px_rgba(15,23,42,0.08)] backdrop-blur">
  <div class="absolute inset-0 bg-[linear-gradient(135deg,rgba(15,23,42,0.03),transparent_40%,rgba(15,23,42,0.02))]"></div>

  <div class="relative flex flex-col gap-6">
    <div class="flex items-start justify-between gap-4">
      <div class="max-w-3xl">
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Generated Briefing</p>
        <h2 class="mt-2 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">{episode.title}</h2>
        <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{episode.summary}</p>
      </div>

      <button
        class="inline-flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:text-slate-950"
        on:click={openHistory}
        aria-label="Open Past Episodes"
        title="Past Episodes"
      >
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 12a8 8 0 1 0 3-6.3" />
          <path d="M4 4v5h5" />
          <path d="M12 7v5l3 2" />
        </svg>
      </button>
    </div>

    <div class="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
      <div class="space-y-4">
        <div class="flex flex-wrap gap-2">
          {#each episode.topics as topic}
            <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">{topic}</span>
          {/each}
        </div>

        <div class="rounded-[1.5rem] border border-slate-200 bg-slate-950 p-5 text-white shadow-inner shadow-slate-950/20">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-400">Live Player</p>
              <p class="mt-2 text-lg font-semibold tracking-tight">Briefing in progress</p>
            </div>
            <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-200">{statusMessage}</span>
          </div>

          <div class="mt-6 flex flex-wrap items-center gap-3">
            <button
              class="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-slate-100"
              on:click={togglePlayback}
            >
              {isPaused ? 'Play briefing' : 'Pause briefing'}
            </button>

            <button
              class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition hover:border-white/20 hover:bg-white/10"
              on:click={rewind}
            >
              -15s
            </button>

            <button
              class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition hover:border-white/20 hover:bg-white/10"
              on:click={fastForward}
            >
              +15s
            </button>
          </div>

          <div class="mt-5 flex items-center gap-3 text-xs text-slate-400">
            <span class="tabular-nums">{formatTime(currentTime)}</span>
            <div class="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
              <div class="h-full rounded-full bg-white/70 transition-all" style={`width: ${progress}%`}></div>
            </div>
            <span class="tabular-nums">{formatTime(duration)}</span>
          </div>

          <audio
            bind:this={audioElement}
            bind:paused={isPaused}
            bind:currentTime={currentTime}
            bind:duration={duration}
            src={episode.audioUrl}
            preload="metadata"
            on:ended={() => {
              isPaused = true;
              statusMessage = 'Briefing finished.';
            }}
          ></audio>

          <p class="mt-4 text-sm leading-6 {errorMessage ? 'text-rose-300' : 'text-slate-300'}">
            {errorMessage || 'Use the transport controls or let the generated briefing play out.'}
          </p>
        </div>
      </div>

      <aside class="grid gap-4">
        <div class="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Session Details</p>

          <dl class="mt-4 space-y-4 text-sm text-slate-600">
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">Created</dt>
              <dd class="font-medium text-slate-950">{new Date(episode.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">Duration</dt>
              <dd class="font-medium text-slate-950">{episode.durationMins} min</dd>
            </div>
            <div class="flex items-center justify-between gap-4">
              <dt class="text-slate-500">Voice</dt>
              <dd class="font-medium text-slate-950">{episode.voice}</dd>
            </div>
          </dl>
        </div>

        <button
          class="justify-self-end text-[0.68rem] font-medium uppercase tracking-[0.28em] text-slate-400 transition hover:text-slate-700"
          on:click={openAdmin}
          aria-label="Open KPI dashboard"
          title="KPI dashboard"
        >
          team metrics
        </button>
      </aside>
    </div>
  </div>
</section>
