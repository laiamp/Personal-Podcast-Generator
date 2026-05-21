<script lang="ts">
  import { goto } from '$app/navigation';

  // --- Missing Setup Helpers & Mock APIs ---
  // Fallback function to generate a tiny valid silent audio data string if missing from your utilities
  function createSilentWavUrl(seconds: number): string {
    return "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==";
  }

  const mockAudioUrl = createSilentWavUrl(6);

  interface Episode {
    id: string;
    title: string;
    createdAt: string;
    topics: string[];
    durationMins: number;
    voice: string;
    summary: string;
    audioUrl: string;
  }

  function createMockEpisode({ id, title, createdAt, topics, durationMins, voice, summary, audioUrl = mockAudioUrl }: Omit<Episode, 'audioUrl'> & { audioUrl?: string }): Episode {
    return {
      id,
      title,
      createdAt,
      topics,
      durationMins,
      voice,
      summary,
      audioUrl,
    };
  }
  
  const initialEpisodes: Episode[] = [
    createMockEpisode({
      id: 'episode-1',
      title: 'Morning Briefing: OpenAI rumor mill, Anthropic updates, and a laser-focused HN digest',
      createdAt: '2026-05-21T06:42:00Z',
      topics: ['Frontier AI Labs (OpenAI/Anthropic)', 'Hacker News Top Stories'],
      durationMins: 10,
      voice: 'alloy',
      summary: '6 segments, 88% completion, commute-friendly pacing.',
    }),
    createMockEpisode({
      id: 'episode-2',
      title: 'Dog-walk digest: AI agent tooling, GPU supply chain, and startup shipping notes',
      createdAt: '2026-05-20T06:30:00Z',
      topics: ['Frontier AI Labs (OpenAI/Anthropic)'],
      durationMins: 5,
      voice: 'echo',
      summary: '4 segments, 5 minute rapid briefing.',
    }),
    createMockEpisode({
      id: 'episode-3',
      title: 'Commute briefing: YC launches, open source drama, and model release context',
      createdAt: '2026-05-19T06:51:00Z',
      topics: ['Hacker News Top Stories'],
      durationMins: 15,
      voice: 'onyx',
      summary: '7 segments, longer deep-dive cut.',
    }),
  ];

  // --- HTML Context Declarations & State Management ---
  let episodes: Episode[] = initialEpisodes;
  let activeEpisodeId: string = initialEpisodes[0].id;
  
  // Audio playback and status states
  let isPaused: boolean = true;
  let currentTime: number = 0;
  let currentDuration: number = 0;
  let audioElement: HTMLAudioElement;
  
  let statusMessage: string = "Paused";
  let errorMessage: string = "";

  // Reactive Values / Computed state
  $: activeEpisode = episodes.find(e => e.id === activeEpisodeId);
  $: activeAudioUrl = activeEpisode ? activeEpisode.audioUrl : "";

  // --- Interaction Handlers ---
  function selectEpisode(episode: Episode) {
    activeEpisodeId = episode.id;
    statusMessage = `Loaded: ${episode.title}`;
    
    // Automatically trigger play on selection once Svelte updates the audio src binding
    setTimeout(() => {
      if (audioElement) {
        audioElement.play()
          .then(() => { isPaused = false; statusMessage = "Playing..."; })
          .catch(() => { statusMessage = "Audio locked. Click Play manually."; });
      }
    }, 50);
  }

  function togglePlayback() {
    if (!audioElement) return;
    if (isPaused) {
      audioElement.play();
      statusMessage = "Playing...";
    } else {
      audioElement.pause();
      statusMessage = "Paused";
    }
  }

  function handleAudioEnded() {
    isPaused = true;
    statusMessage = "Finished playing briefing.";
  }

  function goTo(route: string) {
    statusMessage = `Navigating to ${route}...`;
    goto(`/${route}`);
  }

  // --- Formatting Helpers ---
  function formatDuration(mins: number): string {
    return `${mins}m`;
  }

  function formatDateTime(isoString: string): string {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }
</script>

<svelte:head>
  <title>Podcast</title>
</svelte:head>

<h1>Podcast</h1>

<main class="route route-history">
  <section class="panel route-card history-route-card">
    <div class="section-heading compact">
      <div>
        <p class="eyebrow">History Portal</p>
        <h2>Past Episodes</h2>
      </div>
    </div>

    <div class="history-layout">
      <div class="history-side">
        <div class="history-list">
          {#each episodes as episode}
            <button class="history-item {episode.id === activeEpisodeId ? 'active' : ''}" on:click={() => selectEpisode(episode)}>
              <div class="history-item-main">
                <div class="history-topline">
                  <span class="episode-dot"></span>
                  <h3>{episode.title}</h3>
                </div>
                <p>{episode.summary}</p>
              </div>
              <div class="history-item-meta">
                <span>{formatDateTime(episode.createdAt)}</span>
                <span>{formatDuration(episode.durationMins)}</span>
                <span>{episode.voice}</span>
              </div>
            </button>
          {/each}
        </div>
      </div>

      <div class="history-player">
        <p class="eyebrow">Now Playing</p>
        <h3>{activeEpisode?.title}</h3>
        <p class="history-player-copy">Select any past episode and it will immediately load and start playing.</p>

        <div class="transport-actions stacked">
          <button class="transport-button" on:click={togglePlayback}>{isPaused ? 'Play' : 'Pause'}</button>
          <button class="ghost-button" on:click={() => goTo('generate')}>Generate a new briefing</button>
        </div>

        <div class="audio-shell compact-audio">
          <audio
            bind:this={audioElement}
            bind:paused={isPaused}
            bind:currentTime={currentTime}
            bind:duration={currentDuration}
            src={activeAudioUrl}
            preload="metadata"
            controls
            controlsList="nodownload noplaybackrate"
            on:ended={handleAudioEnded}
          ></audio>
        </div>

        <p class="status-copy {errorMessage ? 'error' : ''}">{errorMessage || statusMessage}</p>
      </div>
    </div>
  </section>
</main>