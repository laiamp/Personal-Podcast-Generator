<script lang="ts">
  import { goto } from '$app/navigation';
  import { tick } from 'svelte';

  const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';
  const backendAudioBaseUrl = `${API_BASE}/audio`;

  function createBackendAudioUrl(filename: string): string {
    return `${backendAudioBaseUrl}/${filename}`;
  }

  const mockAudioUrl = createBackendAudioUrl('test3.mp3');

  interface Episode {
    id: string;
    title: string;
    createdAt: string;
    topics: string[];
    durationMins: number;
    voice: string;
    summary: string;
    audioUrl: string;
    sources?: { id: string; title: string; source_url?: string; scraped_at?: string; summary?: string }[];
  }

  function createMockEpisode({ id, title, createdAt, topics, durationMins, voice, summary, audioUrl = mockAudioUrl, sources = [] }: Omit<Episode, 'audioUrl' | 'sources'> & { audioUrl?: string; sources?: Episode['sources'] }): Episode {
    return {
      id,
      title,
      createdAt,
      topics,
      durationMins,
      voice,
      summary,
      audioUrl,
      sources,
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
      audioUrl: createBackendAudioUrl('test3.mp3'),
      sources: [
        { id: 's1', title: 'OpenAI announces new model', source_url: 'https://openai.com/blog', scraped_at: '2026-05-21T05:00:00Z', summary: 'Company posts details about a minor update and research notes.' },
        { id: 's2', title: 'Anthropic funding report', source_url: 'https://technews.example/anthropic-funding', scraped_at: '2026-05-20T22:10:00Z', summary: 'Coverage of a funding round and hiring plans.' },
        { id: 's3', title: 'Hacker News: Top discussion', source_url: 'https://news.ycombinator.com/item?id=123', scraped_at: '2026-05-21T06:30:00Z', summary: 'HN thread with community reactions to model release.' },
      ],
    }),
    createMockEpisode({
      id: 'episode-2',
      title: 'Dog-walk digest: AI agent tooling, GPU supply chain, and startup shipping notes',
      createdAt: '2026-05-20T06:30:00Z',
      topics: ['Frontier AI Labs (OpenAI/Anthropic)'],
      durationMins: 5,
      voice: 'echo',
      summary: '4 segments, 5 minute rapid briefing.',
      audioUrl: createBackendAudioUrl('test3.mp3'),
      sources: [
        { id: 's4', title: 'GPU supply chain analysis', source_url: 'https://hardware.example/gpu-supply', scraped_at: '2026-05-19T18:00:00Z', summary: 'Report on GPU availability and pricing.' },
        { id: 's5', title: 'Agent tooling roundup', source_url: 'https://devblog.example/agents', scraped_at: '2026-05-19T20:00:00Z', summary: 'Short summaries of new agent frameworks.' },
      ],
    }),
    createMockEpisode({
      id: 'episode-3',
      title: 'Commute briefing: YC launches, open source drama, and model release context',
      createdAt: '2026-05-19T06:51:00Z',
      topics: ['Hacker News Top Stories'],
      durationMins: 15,
      voice: 'onyx',
      summary: '7 segments, longer deep-dive cut.',
      audioUrl: createBackendAudioUrl('test3.mp3'),
      sources: [
        { id: 's6', title: 'YC batch highlights', source_url: 'https://news.example/yc-batch', scraped_at: '2026-05-18T12:00:00Z', summary: 'Selected demo day companies and pitch notes.' },
      ],
    }),
  ];

  let expandedEpisodeId: string | null = null;

  function toggleExpandById(id: string) {
    expandedEpisodeId = expandedEpisodeId === id ? null : id;
  }

  function handleEpisodeRowKeydown(event: KeyboardEvent, episodeId: string) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleExpandById(episodeId);
    }
  }

  // --- HTML Context Declarations & State Management ---
  let episodes: Episode[] = initialEpisodes;
  let activeEpisodeId: string = initialEpisodes[0].id;
  
  // Audio playback and status states
  let isPaused: boolean = true;
  let currentTime: number = 0;
  let currentDuration: number = 0;
  let audioElement: HTMLAudioElement;
  
  let statusMessage: string = "Paused";

  // Reactive Values / Computed state
  $: activeEpisode = episodes.find(e => e.id === activeEpisodeId);
  $: activeAudioUrl = activeEpisode ? activeEpisode.audioUrl : "";

  // --- Interaction Handlers ---
  async function selectEpisode(episode: Episode) {
    activeEpisodeId = episode.id;
    statusMessage = `Loaded: ${episode.title}`;
    if (!audioElement) return;

    await tick();

    try {
      await audioElement.play();
      isPaused = false;
      statusMessage = 'Playing...';
    } catch {
      isPaused = true;
      statusMessage = 'Playback blocked. Use the player controls.';
    }
  }

  async function togglePlayback() {
    if (!audioElement) return;
    if (isPaused) {
      try {
        await audioElement.play();
        isPaused = false;
        statusMessage = 'Playing...';
      } catch {
        statusMessage = 'Playback blocked. Use the browser controls.';
      }
    } else {
      audioElement.pause();
      isPaused = true;
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

  function formatTime(seconds: number): string {
    if (!seconds) return '0:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  }
</script>

<svelte:head>
  <title>Podcast</title>
</svelte:head>


<main class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
  <section class="mx-auto flex w-full max-w-6xl flex-col gap-6 panel route-card history-route-card">
    <div class="flex items-center justify-between gap-4 px-1 text-sm text-slate-500">
      <div>
        <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">History Portal</p>
        <p class="mt-1 text-sm text-slate-500">Browse previously generated briefings and replay them at any time.</p>
      </div>
      <div class="header-actions">
        <button class="ghost-button" on:click={() => goTo('generate')}>Generate</button>
      </div>
    </div>

    <div class="history-layout">
      <div class="history-side">
        <div class="history-list">
          <div class="episodes-grid" role="list">
            {#each episodes as episode}
              <div>
                <div
                  class="episode-row {episode.id === activeEpisodeId ? 'active' : ''}"
                  role="button"
                  tabindex="0"
                  on:click={() => toggleExpandById(episode.id)}
                  on:keydown={(event) => handleEpisodeRowKeydown(event, episode.id)}
                >
                  <div class="episode-play-col">
                    <button
                      class="episode-play-button"
                      on:click|stopPropagation={() => selectEpisode(episode)}
                      aria-label="Play episode"
                      title="Play"
                    >
                      ▶
                    </button>
                  </div>

                  <div class="episode-main">
                    <h3>{episode.title}</h3>
                    <p class="episode-summary">{episode.summary}</p>
                  </div>

                  <div class="episode-meta">
                    <span class="meta-item">{formatDateTime(episode.createdAt)}</span>
                    <span class="meta-item">{formatDuration(episode.durationMins)}</span>
                    <span class="meta-item">{episode.voice}</span>
                  </div>
                </div>

                {#if expandedEpisodeId === episode.id}
                  <div class="sources-row">
                    <div class="sources-list">
                      {#each episode.sources ?? [] as src (src.id)}
                        <div class="source-item">
                          <div class="source-header">
                            <svg class="source-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10 14a3 3 0 004.24 0l3.52-3.52a3 3 0 00-4.24-4.24L10 9.76" />
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14 10a3 3 0 00-4.24 0L6.24 13.76a3 3 0 004.24 4.24L14 14.24" />
                            </svg>
                            <a href={src.source_url} target="_blank" rel="noopener noreferrer" class="source-title">{src.title}</a>
                          </div>
                          <div class="source-meta">{src.scraped_at ? formatDateTime(src.scraped_at) : ''}</div>
                          <p class="source-summary">{src.summary}</p>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      </div>

      <div class="history-player">
          <div class="player-card">
            <!-- <div class="player-left"> -->
              <!-- <div class="player-art">
                <div class="play-overlay">{isPaused ? '▶' : '▌▌'}</div>
              </div> -->
            <!-- </div> -->

            <div class="player-right">
              <div class="flex items-center justify-between">
                <div>
                  <p class="eyebrow">Now Playing</p>
                  <h3 class="player-title">{activeEpisode?.title}</h3>
                  <div class="player-meta">
                    <span class="meta-pill">{activeEpisode ? formatDateTime(activeEpisode.createdAt) : '--'}</span>
                    <span class="meta-pill">{activeEpisode?.voice ?? '--'}</span>
                    <span class="meta-pill">{activeEpisode ? formatDuration(activeEpisode.durationMins) : '--'}</span>
                  </div>
                </div>
              
              </div>

              <div class="mt-4">
                <div class="progress-row">
                  <div class="time">{formatTime(currentTime)}</div>
                  <div class="progress-bar">
                    <div class="progress-fill" style={`width: ${currentDuration ? (currentTime / currentDuration) * 100 : 0}%`} />
                  </div>
                  <div class="time">{formatTime(currentDuration)}</div>
                </div>
              </div>

              <div class="audio-shell compact-audio mt-3">
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

              <!-- <p class="s  tatus-copy">{statusMessage}</p> -->
            </div>
          </div>
      </div>
    </div>
  </section>
</main>

<style>
  .history-layout {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
  }

  .history-side,
  .history-player {
    min-width: 0;
  }

  .history-list {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 14px;
    background: #ffffff;
    overflow: hidden;
  }

  .episodes-grid { display: flex; flex-direction: column; gap: 0.5rem; }
  .episode-row { display: grid; grid-template-columns: 56px 1fr auto; gap: 1rem; align-items: stretch; padding: 0.75rem 1rem; border-bottom: 1px solid rgba(15,23,42,0.04); cursor: pointer; }
  .episode-row.active { background: rgba(99,102,241,0.06); }
  .episode-main h3 { margin: 0; font-size: 1rem; line-height: 1.25; }
  .episode-summary { margin: 0.25rem 0 0; color: #6b7280; font-size: 0.92rem; }
  .episode-meta { display: flex; gap: 0.75rem; color: #6b7280; font-size: 0.88rem; align-items: center; }
  .meta-item { white-space: nowrap; }
  .episode-play-col { display:flex; align-items:stretch; }
  .episode-play-button { display:flex; align-items:center; justify-content:center; width:100%; height:100%; min-height:44px; border-radius:8px; background:#eef2ff; border:none; color:#4f46e5; font-weight:600; cursor:pointer; }
  .episode-play-button:hover { background:#e0e7ff; }

  /* Player card styles */
  .history-player { padding: 0.25rem; }
  .player-card { display: flex; gap: 1rem; align-items: flex-start; padding: 0.75rem; border: 1px solid rgba(15, 23, 42, 0.08); border-radius: 14px; background: #ffffff; }
  .player-left { width: 84px; }
  .player-art { width: 84px; height: 84px; background: linear-gradient(135deg,#eef2ff,#e9d5ff); border-radius: 12px; display:flex; align-items:center; justify-content:center; color:#3730a3; font-weight:700; font-size:1.25rem; position:relative; }
  .play-overlay { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-size:1.25rem; }
  .player-right { flex:1; }
  .player-title { margin:0; font-size:1.05rem; line-height:1.3; }
  .player-meta { margin-top:0.5rem; display:flex; gap:0.5rem; flex-wrap: wrap; }
  .meta-pill { background:#f1f5f9; color:#475569; padding:0.25rem 0.5rem; border-radius:999px; font-size:0.75rem; }
  .progress-row { display:flex; align-items:center; gap:0.75rem; }
  .progress-bar { flex:1; height:8px; background:#f1f5f9; border-radius:999px; overflow:hidden; }
  .progress-fill { height:100%; background:linear-gradient(90deg,#60a5fa,#7c3aed); }
  .time { font-size:0.75rem; color:#6b7280; width:42px; text-align:center; }
  .transport-actions { display:flex; gap:0.5rem; flex-wrap: wrap; justify-content: flex-end; }
  .transport-button { background:#4f46e5; color:white; border:none; padding:0.5rem 0.75rem; min-height:44px; border-radius:8px; cursor:pointer; }
  .ghost-button { background:transparent; border:1px solid #e6e9ef; padding:0.45rem 0.6rem; min-height:44px; border-radius:8px; cursor:pointer; }
  .audio-shell audio { width: 100%; }
  .status-copy { margin-top: 0.75rem; }

  /* expand handled by clicking the episode row now */

  .sources-row { padding: 0.75rem 1rem; background: #fbfdff; border-left: 3px solid rgba(99,102,241,0.12); }
  .sources-list { display:flex; flex-direction:column; gap:0.5rem; }
  .source-item { padding:0.5rem 0; border-bottom:1px solid rgba(15,23,42,0.03); }
  .source-header { display:flex; align-items:flex-start; gap:0.5rem; }
  .source-icon { width:18px; height:18px; color:#64748b; flex:0 0 18px; }
  .source-title { color:#0f172a; font-weight:600; text-decoration:none; overflow-wrap:anywhere; }
  .source-title:hover { text-decoration:underline; }
  .source-summary { margin:0.25rem 0 0; color:#6b7280; font-size:0.92rem; }
  .source-meta { font-size:0.78rem; color:#94a3b8; }

  @media (min-width: 1024px) {
    .history-layout {
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.95fr);
      gap: 1.25rem;
      align-items: start;
    }

    .history-player {
      padding: 0;
      position: sticky;
      top: 1rem;
    }
  }

  @media (max-width: 768px) {
    .episode-row {
      grid-template-columns: 48px minmax(0, 1fr);
      gap: 0.75rem;
      padding: 0.75rem;
    }

    .episode-main h3 {
      font-size: 0.95rem;
      line-clamp: 2;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .episode-summary {
      font-size: 0.84rem;
      line-clamp: 2;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .episode-meta {
      grid-column: 1 / -1;
      padding-left: 3.15rem;
      gap: 0.5rem;
      flex-wrap: wrap;
      font-size: 0.8rem;
    }

    .player-card {
      flex-direction: column;
      padding: 0.75rem;
    }

    .player-left {
      width: 100%;
    }

    .player-art {
      width: 100%;
      height: 72px;
    }

    .player-title {
      font-size: 0.98rem;
      margin-top: 0.1rem;
    }

    .transport-actions {
      width: 100%;
      justify-content: flex-start;
      margin-top: 0.75rem;
    }

    .transport-button,
    .ghost-button {
      flex: 1;
      min-width: 110px;
    }

    .time {
      width: 36px;
      font-size: 0.72rem;
    }

    .sources-row {
      padding: 0.65rem 0.75rem;
    }
  }
</style>