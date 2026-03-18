// Shared reactive store for subjects.
// Fetches the list exactly once per session; components call ensureSubjectsLoaded on mount.
// All mutations flow through store helpers so components never re-fetch.

import { fetchSubjectData } from './api.js';

export const appState = $state({
    subjects: [],         // full fields: subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at
    subjectsLoaded: false,
});

// Guard flag prevents duplicate in-flight requests
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

// ── Subject store helpers ─────────────────────────────────────────────────────

// Appends appState.subjects with new object
export function storeAddSubject(subject) {
    appState.subjects.push(subject);
}

// Assigns the updates to the specified object in appState.subjects
export function storeUpdateSubject(id, updates) {
    const found = appState.subjects.find(s => s.subject_id === id);
    if (found) Object.assign(found, updates);
}

// Removes the specified object from appState.subjects
export function storeRemoveSubject(id) {
    appState.subjects = appState.subjects.filter(s => s.subject_id !== id);
}
