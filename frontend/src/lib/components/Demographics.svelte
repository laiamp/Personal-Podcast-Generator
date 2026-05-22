<script lang="ts">
  export let gender: Record<string, number> = { male: 0, female: 0, other: 0, undisclosed: 0 };
  export let ageBuckets: { label: string; value: number }[] = [];

  const total = Object.values(gender).reduce((a, b) => a + b, 0) || 1;
  const maxAge = Math.max(...ageBuckets.map((b) => b.value), 1);
  const maxGender = Math.max(...Object.values(gender), 1);
</script>

<section class="rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)]">
  <p class="text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-400">Audience</p>
  <h2 class="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Demographics</h2>

  <div class="mt-4 grid gap-4 md:grid-cols-2">
    <div>
      <p class="text-sm text-slate-600 mb-3">Gender distribution</p>
      <div class="space-y-3">
        {#each Object.entries(gender) as [k, v]}
          <div>
            <div class="flex items-center justify-between text-xs text-slate-600 mb-1">
              <span class="capitalize">{k.replace('_', ' ')}</span>
              <span>{Math.round((v / total) * 100)}%</span>
            </div>
            <div class="h-3 w-full rounded bg-slate-100">
              <div class="h-full rounded bg-gradient-to-r from-indigo-500 to-violet-500" style={`width: ${Math.round((v / maxGender) * 100)}%`}></div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <div>
      <p class="text-sm text-slate-600 mb-3">Age distribution</p>
      <div class="space-y-2">
        {#each ageBuckets as bucket}
          <div class="flex items-center gap-3">
            <div class="w-20 text-xs text-slate-600">{bucket.label}</div>
            <div class="h-4 w-full rounded bg-slate-100">
              <div class="h-full rounded bg-emerald-400" style={`width: ${Math.round((bucket.value / maxAge) * 100)}%`}></div>
            </div>
            <div class="w-12 text-right text-xs text-slate-500">{bucket.value}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>
