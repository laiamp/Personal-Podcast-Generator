<script lang="ts">
  export let data: number[][] = [];
  export let days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  export let hours = Array.from({ length: 24 }, (_, i) => i);

  const flat = data.flat();
  const min = flat.length ? Math.min(...flat) : 0;
  const max = flat.length ? Math.max(...flat) : 0;
  const normalize = (v: number) => (max === min ? 0 : (v - min) / (max - min));

  function bgFor(v: number) {
    const n = Math.round(normalize(v) * 100);
    return `hsl(210 70% ${95 - n * 0.6}%)`;
  }
</script>

<section class="rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)]">
  <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-400">Listening Pulse</p>
  <h2 class="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Hourly Heatmap</h2>

  <div class="mt-4 overflow-auto">
    <div class="min-w-[420px]">
      <div class="grid items-center gap-2" style={`grid-template-columns: 5rem repeat(${hours.length}, 2.5rem);`}>
        <div></div>
        {#each hours as h}
          <div class="text-xs text-slate-400 text-center">{h}</div>
        {/each}
      </div>

      {#each days as day, di}
        <div class="grid items-center gap-2 mt-2" style={`grid-template-columns: 5rem repeat(${hours.length}, 2.5rem);`}>
          <div class="text-sm font-medium text-slate-600">{day}</div>
          {#each data[di] ?? Array.from({length:hours.length},()=>0) as v, hi}
            <div
              class="w-10 h-6 rounded-sm border border-slate-100"
              title={`${day} ${hours[hi]}:00 — ${v}`}
              style="background: {bgFor(v)};"
            />
          {/each}
        </div>
      {/each}
    </div>
  </div>

  <div class="mt-4 flex items-center gap-3 text-sm text-slate-600">
    <div class="flex items-center gap-2">
      <span class="inline-block w-6 h-3" style="background: {bgFor(min)};"></span>
      <span>Low</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="inline-block w-6 h-3" style="background: {bgFor((min+max)/2)};"></span>
      <span>Medium</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="inline-block w-6 h-3" style="background: {bgFor(max)};"></span>
      <span>Peak</span>
    </div>
  </div>
</section>
