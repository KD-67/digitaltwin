<script>
  import { onMount } from 'svelte';

  let message = 'Loading...';

  async function fetchHello() {
    const res = await fetch('http://localhost:8000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '{ hello }' }),
    });
    const { data } = await res.json();
    message = data.hello;
  }

  onMount(fetchHello);
</script>

<main>
  <h1>Digital Twin</h1>
  <p>{message}</p>
</main>

<style>
  main {
    font-family: sans-serif;
    text-align: center;
    padding: 2rem;
  }
</style>
