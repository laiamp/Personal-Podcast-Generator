<script lang="ts">
  const metrics = [
    {
      label: 'Total Streams',
      value: '12.5k',
      delta: '+18% vs last month',
      note: 'Listeners are coming back consistently during commute windows.',
      tone: 'from-slate-950 to-slate-700',
    },
    {
      label: 'Avg. Completion Rate',
      value: '85%',
      delta: '+6 pts week over week',
      note: 'Most people finish before they arrive, which is the core product promise.',
      tone: 'from-emerald-500 to-teal-500',
    },
    {
      label: 'Active Daily Commuters',
      value: '3.2k',
      delta: '+410 this week',
      note: 'Morning usage is concentrated and sticky across repeat listeners.',
      tone: 'from-amber-500 to-orange-500',
    },
    {
      label: 'Avg. Listen Length',
      value: '22 min',
      delta: '+3 min per session',
      note: 'Right-sized for a train ride, coffee run, or school dropoff.',
      tone: 'from-cyan-500 to-sky-500',
    },
  ];

  const signalBands = [
    { label: 'Morning peak', value: '7:00 - 9:00', strength: 92 },
    { label: 'Lunch rebound', value: '11:30 - 1:00', strength: 64 },
    { label: 'Evening catch-up', value: '5:30 - 7:00', strength: 71 },
  ];

  const topSignals = [
    'AI labs / frontier updates',
    'Hacker News top stories',
    'Startup shipping notes',
    'Model release context',
  ];

  import TimeHeatmap from '$lib/components/TimeHeatmap.svelte';
  import Demographics from '$lib/components/Demographics.svelte';
  import MonthlyUsersLineChart from '$lib/components/MonthlyUsersLineChart.svelte';

  const heatmapHours = Array.from({ length: 24 }, (_, i) => i); // 0..23

  function generateHeatmap(hoursArr: number[]) {
    const days = 7;
    const hoursCount = hoursArr.length;
    const mat = Array.from({ length: days }, () => Array.from({ length: hoursCount }, () => Math.floor(Math.random() * 20 + 5)));

    const applyBand = (start: number, end: number, strength: number, dow = [0,1,2,3,4]) => {
      for (const d of dow) {
        for (let hv = start; hv <= end; hv++) {
          const idx = hoursArr.indexOf(hv);
          if (idx >= 0) mat[d][idx] = Math.max(mat[d][idx], strength);
        }
      }
    };

    applyBand(7, 9, 92);   // morning peak (Mon-Fri)
    applyBand(11, 13, 64); // lunch rebound

    // small weekend morning boost
    applyBand(9, 11, 50, [5,6]);

    return mat;
  }

  const listeningHeatmap = generateHeatmap(heatmapHours);

  // Mock demographics data
  const demographicsGender = {
    male: 4200,
    female: 3200,
    other: 180,
    undisclosed: 400,
  };

  const demographicsAge = [
    { label: '18-24', value: 900 },
    { label: '25-34', value: 3600 },
    { label: '35-44', value: 1200 },
    { label: '45-54', value: 600 },
    { label: '55+', value: 380 },
  ];

  const monthlyUsers = [
    { month: 'Jan', users: 980 },
    { month: 'Feb', users: 1120 },
    { month: 'Mar', users: 1360 },
    { month: 'Apr', users: 1710 },
    { month: 'May', users: 2030 },
    { month: 'Jun', users: 2460 },
    { month: 'Jul', users: 2890 },
    { month: 'Aug', users: 3320 },
  ];
</script>

<svelte:head>
  <title>KPIs</title>
</svelte:head>

<main class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
  <section class="mx-auto flex w-full max-w-7xl flex-col gap-6">
    <header class="relative overflow-hidden rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_32px_80px_rgba(15,23,42,0.08)] backdrop-blur">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(15,23,42,0.06),transparent_30%),radial-gradient(circle_at_top_left,rgba(16,185,129,0.12),transparent_28%)]"></div>

      <div class="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-3xl">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Internal Product Success Metrics</p>
          <h1 class="mt-3 text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">Team Dashboard</h1>
          <p class="mt-4 max-w-2xl text-sm leading-6 text-slate-600">
            A compact view of how the podcast generator is performing in demo conditions: reach, retention, and the habits
            that matter most for commuting listeners.
          </p>
        </div>

        <div class="grid gap-3 sm:grid-cols-3 lg:max-w-2xl lg:grid-cols-3">
          <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-slate-400">Sessions</p>
            <strong class="mt-2 block text-2xl font-semibold text-slate-950">128</strong>
            <p class="mt-1 text-xs text-slate-500">today</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-slate-400">Conversion</p>
            <strong class="mt-2 block text-2xl font-semibold text-slate-950">38%</strong>
            <p class="mt-1 text-xs text-slate-500">generate clicks</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <p class="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-slate-400">Retention</p>
            <strong class="mt-2 block text-2xl font-semibold text-slate-950">85%</strong>
            <p class="mt-1 text-xs text-slate-500">completion rate</p>
          </div>
        </div>
      </div>
    </header>

    <div class="grid gap-6 xl:grid-cols-[1.7fr_0.9fr]">
      <section class="grid gap-4 sm:grid-cols-2">
        {#each metrics as metric}
          <article class="group relative overflow-hidden rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)] transition hover:-translate-y-0.5 hover:shadow-[0_28px_60px_rgba(15,23,42,0.1)]">
            <div class={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${metric.tone}`}></div>
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-slate-400">{metric.label}</p>
                <strong class="mt-3 block text-4xl font-semibold tracking-tight text-slate-950">{metric.value}</strong>
              </div>
              <span class="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">{metric.delta}</span>
            </div>
            <p class="mt-5 max-w-md text-sm leading-6 text-slate-600">{metric.note}</p>
          </article>
        {/each}
      </section>

      <aside class="grid gap-4">

        <section class="rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)]">
          <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-400">Top Signals</p>
          <h2 class="mt-3 text-2xl font-semibold tracking-tight text-slate-950">What listeners gravitate toward</h2>
          <div class="mt-5 flex flex-wrap gap-2">
            {#each topSignals as signal}
              <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">{signal}</span>
            {/each}
          </div>

          <div class="mt-6 rounded-2xl bg-slate-50 p-4">
            <p class="text-sm leading-6 text-slate-600">
              The dashboard is intentionally restrained so it reads as an internal demo panel, not a consumer-facing analytics
              product.
            </p>
          </div>
        </section>
      </aside>
    </div>

    <MonthlyUsersLineChart points={monthlyUsers} />

    <section class="mt-4">
      <TimeHeatmap data={listeningHeatmap} hours={heatmapHours} />

      <div class="mt-6">
        <Demographics gender={demographicsGender} ageBuckets={demographicsAge} />
      </div>
    </section>
  </section>
</main>
