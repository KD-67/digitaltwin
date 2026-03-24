// Shared reactive store for subjects, markers, and measurements.
// Fetches each list exactly once per session; components call ensureXxxLoaded on mount.
// All mutations flow through store helpers so components never re-fetch.

import { fetchSubjectData, fetchMarkerData, fetchMeasurementsBySubject } from './api.js';

export const appState = $state({
    subjects: [],          // full fields: subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at
    subjectsLoaded: false,
    markers: [],           // full fields: marker_id, marker_name, description, unit, volatility_class, storage_type, created_at
    markersLoaded: false,
    selectedSubject: null, // set before navigating to #subject-detail
    measurementsBySubject: {},  // { "subj_001": Measurement[], ... }  (lazy per-subject cache)
    sandboxSubjectId: null,    // set when user submits subject selection in trajectory sandbox
    sandboxMarkerIds: [],   // marker_ids selected for display in trajectory sandbox
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

// ── Measurements ──────────────────────────────────────────────────────────────
// measurementsBySubject is a plain object keyed by subject_id.
// Presence of the key (even as an empty array) means that subject's data is loaded.

const measurementsLoadingFor = new Set();  // non-reactive semaphore; just prevents duplicate fetches

export async function ensureMeasurementsLoaded(subject_id) {
    if (subject_id in appState.measurementsBySubject || measurementsLoadingFor.has(subject_id)) return;
    measurementsLoadingFor.add(subject_id);
    try {
        const measurements = await fetchMeasurementsBySubject(subject_id);
        appState.measurementsBySubject[subject_id] = measurements;
    } finally {
        measurementsLoadingFor.delete(subject_id);
    }
}

export function storeAddMeasurement(subject_id, measurement) {
    const current = appState.measurementsBySubject[subject_id] ?? [];
    appState.measurementsBySubject[subject_id] = [measurement, ...current];
}

export function storeRemoveMeasurement(subject_id, marker_id, measured_at) {
    const current = appState.measurementsBySubject[subject_id] ?? [];
    appState.measurementsBySubject[subject_id] = current.filter(
        m => !(m.marker_id === marker_id && m.measured_at === measured_at)
    );
}
