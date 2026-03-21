<script>
  import { onMount } from 'svelte';
  let currentPage = window.location.hash.slice(1) || "home";

  // Svelte components:
  import Home from './components/nav_components.svelte/home.svelte';
  import Pipeline from './components/nav_components.svelte/pipeline.svelte';
  import Acquisition from './components/pipeline_components/acquisition.svelte';
  import Management from './components/pipeline_components/management.svelte';
  import Analysis from './components/pipeline_components/analysis.svelte';
  import Prediction from './components/pipeline_components/prediction.svelte';
  import Interpretation from './components/pipeline_components/interpretation.svelte';
  import Sandbox from './components/nav_components.svelte/sandbox_components/sandbox.svelte';
  import TrajectorySandbox from './components/nav_components.svelte/sandbox_components/trajectory_sandbox.svelte';
  import TestSandbox from './components/nav_components.svelte/sandbox_components/test_sandbox.svelte';
  import Architecture from './components/nav_components.svelte/architecture.svelte';
  import Help from './components/nav_components.svelte/help.svelte';
  import Subjects from './components/pipeline_components/acquisition_components/subjects.svelte';
  import SubjectDetail from './components/pipeline_components/acquisition_components/subject_detail.svelte';
  import Data from './components/pipeline_components/acquisition_components/data.svelte';

  // Assets:
  import LogoIcon from '/src/assets/logo_icon.svg';

  // Functions:
    onMount(() => {
      window.addEventListener("hashchange", () => {
        currentPage = window.location.hash.slice(1) || "home";
      });
    });
</script>

<main>
  <header>

    <div id="titleandlogo-container">
      <img id="logo" src="{LogoIcon}" alt="logo">
      <div id="title-container">
        <p id="title">Human Digital Twin</p>
      </div>
    </div>

    <nav>
      <a class="nav-link" href="#home">Home</a>

      <div class="dropdown">
        <a class="nav-link" id="nav-comp-dropdown" href="#pipeline">Pipeline</a>
        <div id="dropdown-menu">
          <a class="dropdown-content" href="#acquisition">Aquisition</a>
          <a class="dropdown-content" href="#management">Management</a>
          <a class="dropdown-content" href="#analysis">Analysis</a>
          <a class="dropdown-content" href="#prediction">Prediction</a>
          <a class="dropdown-content" href="#interpretation">Interpretation</a>
        </div>
      </div>

      <a class="nav-link" href="#sandbox">Sandbox</a>
      <a class="nav-link" href="#architecture">Architecture</a>
      <a class="nav-link" href="#help">Help</a>
    </nav>

  </header>
  {#if currentPage == "home"}
  <Home />
  {:else if currentPage == "pipeline"}
  <Pipeline />
  {:else if currentPage == "acquisition"}
  <Acquisition />
  {:else if currentPage == "management"}
  <Management />
  {:else if currentPage == "analysis"}
  <Analysis />
  {:else if currentPage == "prediction"}
  <Prediction />
  {:else if currentPage == "interpretation"}
  <Interpretation />
  {:else if currentPage == "sandbox"}
  <Sandbox />
  {:else if currentPage == "trajectory_sandbox"}
  <TrajectorySandbox />
  {:else if currentPage == "test_sandbox"}
  <TestSandbox />
  {:else if currentPage == "architecture"}
  <Architecture />
  {:else if currentPage == "help"}
  <Help />
  {:else if currentPage == "data"}
  <Data />
  {:else if currentPage == "subjects"}
  <Subjects />
  {:else if currentPage == "subject_detail"}
  <SubjectDetail />
  {/if}
</main>

<style>
  * {
    margin: 0;
    padding: 0;
  }

  main {
    font-family: sans-serif;
    text-align: center;
    padding: 1.5rem;
  }



  #titleandlogo-container {
    display: flex;
  }

  #logo {
    height: 100px;
  }

  #title-container {
    display: flex;
    align-items: center;
  }

  nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 8px;
  }

  .nav-link {
    border: 1px solid black;
    background-color: transparent;
    color: black;
    border: none;
    padding: 10px 15px;
    cursor: pointer;
    display: inline-block;
  }

  .nav-link:hover {
    color: blue;
    transform: scale(110%);
  }

  .dropdown {
    position: relative;
  }

  #dropdown-menu {
    position: absolute;
    text-align: left;
    top: calc(100% + .25rem);
    left: 0;
    background-color: white;
    box-shadow: 0 2px 5px rgb(0, 0, 0, 0.1);
    min-width: 100%;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-6px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  }

  .dropdown:hover #dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  .dropdown-content {
    display: block;
    padding: 8px 15px;
    color: black;
    white-space: nowrap;
  }

  .dropdown-content:hover {
    background-color: #f0f0f0;
  }

</style>
