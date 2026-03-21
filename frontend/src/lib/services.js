// Service layer — wraps API calls with automatic appState store updates.
// Components import mutating operations from here instead of api.js directly.

import {
    createSubject as apiCreateSubject,
    updateSubject as apiUpdateSubject,
    deleteSubject as apiDeleteSubject,
    createMarker as apiCreateMarker,
    updateMarker as apiUpdateMarker,
    deleteMarker as apiDeleteMarker,
    addMeasurement as apiAddMeasurement,
    deleteMeasurement as apiDeleteMeasurement,
} from './api.js';

import {
    storeAddSubject, storeUpdateSubject, storeRemoveSubject,
    storeAddMarker, storeUpdateMarker, storeRemoveMarker,
    storeAddMeasurement, storeRemoveMeasurement,
} from './stores.svelte.js';

// ── Utilities ─────────────────────────────────────────────────────────────────

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

export async function createMarker({ marker_name, description, unit, volatility_class, storage_type = 'sparse' }) {
    const marker_id = await apiCreateMarker({ markerName: marker_name, description, unit, volatilityClass: volatility_class, storageType: storage_type });
    storeAddMarker({ marker_id, marker_name, description, unit, volatility_class, storage_type, created_at: new Date().toISOString() });
    return marker_id;
}

export async function updateMarker(marker_id, updates) {
    const { marker_name, description, unit, volatility_class, storage_type } = updates;
    await apiUpdateMarker(marker_id, { markerName: marker_name, description, unit, volatilityClass: volatility_class, storageType: storage_type });
    storeUpdateMarker(marker_id, updates);
}

export async function deleteMarker(marker_id) {
    await apiDeleteMarker(marker_id);
    storeRemoveMarker(marker_id);
}

// ── Measurements ──────────────────────────────────────────────────────────────

export async function addMeasurement({ subject_id, marker_id, measured_at, value, quality, notes }) {
    const measurement = await apiAddMeasurement({ subject_id, marker_id, measured_at, value, quality, notes });
    storeAddMeasurement(subject_id, measurement);
    return measurement;
}

export async function deleteMeasurement(subject_id, marker_id, measured_at) {
    await apiDeleteMeasurement(subject_id, marker_id, measured_at);
    storeRemoveMeasurement(subject_id, marker_id, measured_at);
}
