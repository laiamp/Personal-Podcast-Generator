<script lang="ts">
  interface MonthlyUserPoint {
    month: string;
    users: number;
  }

  export let title = 'Current active users by month';
  export let subtitle = 'Jan to Aug snapshot';
  export let points: MonthlyUserPoint[] = [];

  const chartWidth = 860;
  const chartHeight = 250;
  const chartPaddingX = 52;
  const chartPaddingY = 26;

  $: safePoints = points.length > 1 ? points : [
    { month: 'N/A', users: 0 },
    { month: 'N/A', users: 0 },
  ];

  $: minUsers = Math.min(...safePoints.map((point) => point.users));
  $: maxUsers = Math.max(...safePoints.map((point) => point.users));
  $: yRange = Math.max(1, maxUsers - minUsers);

  $: chartPoints = safePoints
    .map((point, index) => {
      const x = chartPaddingX + (index * (chartWidth - chartPaddingX * 2)) / (safePoints.length - 1);
      const y = chartHeight - chartPaddingY - ((point.users - minUsers) / yRange) * (chartHeight - chartPaddingY * 2);
      return `${x},${y}`;
    })
    .join(' ');

  $: yTicks = Array.from({ length: 4 }, (_, i) => {
    const value = minUsers + (i * yRange) / 3;
    const y = chartHeight - chartPaddingY - (i / 3) * (chartHeight - chartPaddingY * 2);
    return { value: Math.round(value), y };
  });
</script>

<section class="rounded-[1.75rem] border border-slate-200/80 bg-white p-5 shadow-[0_20px_50px_rgba(15,23,42,0.06)]">
  <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <p class="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-slate-400">Growth Trend</p>
      <h2 class="mt-2 text-2xl font-semibold tracking-tight text-slate-950">{title}</h2>
    </div>
    <p class="text-xs text-slate-500">{subtitle}</p>
  </div>

  <div class="mt-5 overflow-x-auto">
    <svg class="min-w-[680px]" viewBox={`0 0 ${chartWidth} ${chartHeight}`} aria-label="Monthly active users line chart" role="img">
      <rect x="0" y="0" width={chartWidth} height={chartHeight} rx="18" fill="#f8fafc" />

      {#each yTicks as tick}
        <line x1={chartPaddingX} y1={tick.y} x2={chartWidth - chartPaddingX} y2={tick.y} stroke="#e2e8f0" stroke-width="1" />
        <text x={chartPaddingX - 10} y={tick.y + 4} text-anchor="end" font-size="11" fill="#64748b">{tick.value}</text>
      {/each}

      <polyline fill="none" stroke="#0f766e" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" points={chartPoints} />

      {#each safePoints as point, i}
        {@const cx = chartPaddingX + (i * (chartWidth - chartPaddingX * 2)) / (safePoints.length - 1)}
        {@const cy = chartHeight - chartPaddingY - ((point.users - minUsers) / yRange) * (chartHeight - chartPaddingY * 2)}
        <circle cx={cx} cy={cy} r="5" fill="#0f766e" />
        <circle cx={cx} cy={cy} r="10" fill="#0f766e" fill-opacity="0.12" />
        <text x={cx} y={chartHeight - 6} text-anchor="middle" font-size="11" fill="#64748b">{point.month}</text>
      {/each}
    </svg>
  </div>
</section>
