<script lang="ts">
  export let statusMessage = 'Gathering morning headers...';
</script>

<section class="relative overflow-hidden rounded-[2rem] border border-slate-200/70 bg-white/90 px-8 py-14 text-slate-950 shadow-[0_32px_80px_rgba(15,23,42,0.08)] backdrop-blur">
  <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(15,23,42,0.04),_transparent_55%)]"></div>

  <div class="relative mx-auto flex max-w-2xl flex-col items-center text-center">
    <div class="loader-rings" aria-hidden="true">
      <span></span>
      <span></span>
      <span></span>
    </div>

    <p class="mt-8 text-[0.68rem] font-semibold uppercase tracking-[0.32em] text-slate-500">Loading podcast</p>
    <h2 class="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Curating the commute briefing</h2>
    <p class="mt-4 max-w-xl text-sm leading-6 text-slate-600">{statusMessage}</p>

    <div class="mt-10 flex w-full max-w-md items-center gap-2" aria-hidden="true">
      <span class="loader-bar"></span>
      <span class="loader-bar"></span>
      <span class="loader-bar"></span>
    </div>
  </div>
</section>

<style>
  .loader-rings {
    position: relative;
    height: 6.5rem;
    width: 6.5rem;
  }

  .loader-rings span {
    position: absolute;
    inset: 0;
    border-radius: 9999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    animation: ringPulse 2.4s ease-in-out infinite;
  }

  .loader-rings span:nth-child(2) {
    inset: 1rem;
    animation-delay: 0.2s;
  }

  .loader-rings span:nth-child(3) {
    inset: 2rem;
    animation-delay: 0.4s;
  }

  .loader-bar {
    height: 0.5rem;
    flex: 1;
    border-radius: 9999px;
    background: linear-gradient(90deg, rgba(15, 23, 42, 0.08), rgba(15, 23, 42, 0.24), rgba(15, 23, 42, 0.08));
    animation: barPulse 1.4s ease-in-out infinite;
  }

  .loader-bar:nth-child(2) {
    animation-delay: 0.14s;
  }

  .loader-bar:nth-child(3) {
    animation-delay: 0.28s;
  }

  @keyframes ringPulse {
    0%,
    100% {
      transform: scale(0.96);
      opacity: 0.35;
    }

    50% {
      transform: scale(1.04);
      opacity: 1;
    }
  }

  @keyframes barPulse {
    0%,
    100% {
      transform: translateY(0);
      opacity: 0.45;
    }

    50% {
      transform: translateY(-2px);
      opacity: 1;
    }
  }
</style>
