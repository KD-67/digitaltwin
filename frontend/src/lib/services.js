// Service layer — wraps API calls with automatic appState store updates.
// Components import mutating operations from here instead of api.js directly.

import {
    createSubject as apiCreateSubject,
    updateSubject as apiUpdateSubject,
    deleteSubject as apiDeleteSubject,
    createMarker as apiCreateMarker,
    updateMarker as apiUpdateMarker,
    deleteMarker as apiDeleteMarker,
} from './api.js';

import {
    storeAddSubject, storeUpdateSubject, storeRemoveSubject,
    storeAddMarker, storeUpdateMarker, storeRemoveMarker,
} from './stores.svelte.js';

// ── Utilities ────────────────────────────────────────────────────────────────

export function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString(undefined, { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// ── Subjects ──────────────────────────────────────────────────────────────────

export async function createSubject({ first_name, last_name, sex, dob, email, phone, notes }) {
    const subject_id = await apiCreateSubject({ firstName: first_name, lastName: last_name, sex, dob, email, phone, notes });
    storeAddSubject({ subject_id, first_name, last_name, sex, dob, email, phone, notes, created_at: new Date().toISOString() });
    return subject_id;
}

export async function updateSubject(subject_id, updates) {
    const { first_name, last_name, sex, dob, email, phone, notes } = updates;
    await apiUpdateSubject(subject_id, { firstName: first_name, lastName: last_name, sex, dob, email, phone, notes });
    storeUpdateSubject(subject_id, updates);
}

export async function deleteSubject(subject_id) {
    await apiDeleteSubject(subject_id);
    storeRemoveSubject(subject_id);
}

// ── Markers ───────────────────────────────────────────────────────────────────

export async function createMarker({ marker_name, description, unit, volatility_class }) {
    const marker_id = await apiCreateMarker({ markerName: marker_name, description, unit, volatilityClass: volatility_class });
    storeAddMarker({ marker_id, marker_name, description, unit, volatility_class, created_at: new Date().toISOString() });
    return marker_id;
}

export async function updateMarker(marker_id, updates) {
    const { marker_name, description, unit, volatility_class } = updates;
    await apiUpdateMarker(marker_id, { markerName: marker_name, description, unit, volatilityClass: volatility_class });
    storeUpdateMarker(marker_id, updates);
}

export async function deleteMarker(marker_id) {
    await apiDeleteMarker(marker_id);
    storeRemoveMarker(marker_id);
}
