// Shared reactive store for subjects and markers.
// Fetches the list exactly once per session; components call ensureXxxLoaded on mount.
// All mutations flow through store helpers so components never re-fetch.

import { fetchSubjectData, fetchMarkerData } from './api.js';

export const appState = $state({
    subjects: [],         // full fields: subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at
    subjectsLoaded: false,
    markers: [],          // full fields: marker_id, marker_name, description, unit, volatility_class, created_at
    markersLoaded: false,
});

// ── Subjects ──────────────────────────────────────────────────────────────────

let subjectsLoading = false;

export async function ensureSubjectsLoaded() {
    if (appState.subjectsLoaded || subjectsLoading) return;
    subjectsLoading = true;
    try {
        const subs = await fetchSubjectData();
        appState.subjects = subs;
        appState.subjectsLoaded = true;
    } finally {
        subjectsLoading = false;
    }
}

export function storeAddSubject(subject) {
    appState.subjects.push(subject);
}

export function storeUpdateSubject(id, updates) {
    const found = appState.subjects.find(s => s.subject_id === id);
    if (found) Object.assign(found, updates);
}

export function storeRemoveSubject(id) {
    appState.subjects = appState.subjects.filter(s => s.subject_id !== id);
}

// ── Markers ───────────────────────────────────────────────────────────────────

let markersLoading = false;

export async function ensureMarkersLoaded() {
    if (appState.markersLoaded || markersLoading) return;
    markersLoading = true;
    try {
        const markers = await fetchMarkerData();
        appState.markers = markers;
        appState.markersLoaded = true;
    } finally {
        markersLoading = false;
    }
}

export function storeAddMarker(marker) {
    appState.markers.push(marker);
}

export function storeUpdateMarker(id, updates) {
    const found = appState.markers.find(m => m.marker_id === id);
    if (found) Object.assign(found, updates);
}

export function storeRemoveMarker(id) {
    appState.markers = appState.markers.filter(m => m.marker_id !== id);
}
