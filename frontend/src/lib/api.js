// Shared GraphQL query constants and typed fetch wrappers.
// All fetch functions return snake_case objects; camelCase normalisation happens here.
// Components import these instead of embedding query strings inline.

import { gql } from "./gql.js";


// ── Subjects ──────────────────────────────────────────────────────────────────

const SUBJECT_FIELD_MAP = {
    subject_id: 'subjectId',
    first_name: 'firstName',
    last_name:  'lastName',
    sex:        'sex',
    dob:        'dob',
    email:      'email',
    phone:      'phone',
    notes:      'notes',
    created_at: 'createdAt',
};

const ALL_SUBJECT_FIELDS = ['subject_id', 'first_name', 'last_name', 'sex', 'dob', 'email', 'phone', 'notes', 'created_at'];

/**
 * Fetches subject(s) with the specified fields.
 * subjectId=null → returns array of all subjects.
 * subjectId="some_id" → returns a single object or null.
 * fields defaults to all subject fields.
 */
export async function fetchSubjectData(subjectId = null, fields = ALL_SUBJECT_FIELDS) {
    const gqlFields = fields.map(f => SUBJECT_FIELD_MAP[f]).join(' ');
    function mapObj(obj) {
        const result = {};
        for (const f of fields) result[f] = obj[SUBJECT_FIELD_MAP[f]];
        return result;
    }
    if (subjectId === null) {
        const data = await gql(`query { subjects { ${gqlFields} } }`);
        return data.subjects.map(mapObj);
    } else {
        const data = await gql(
            `query($id: String!) { subject(subjectId: $id) { ${gqlFields} } }`,
            { id: subjectId }
        );
        return data.subject ? mapObj(data.subject) : null;
    }
}

// ── Subject mutations ─────────────────────────────────────────────────────────

/** Returns subject_id string */
export async function createSubject(input) {
    const data = await gql(
        `mutation($input: SubjectInput!) { createSubject(input: $input) { subjectId } }`,
        { input }
    );
    return data.createSubject.subjectId;
}

export async function updateSubject(subjectId, input) {
    await gql(
        `mutation($id: String!, $input: SubjectInput!) { updateSubject(subjectId: $id, input: $input) { subjectId } }`,
        { id: subjectId, input }
    );
}

export async function deleteSubject(subjectId) {
    await gql(
        `mutation($id: String!) { deleteSubject(subjectId: $id) }`,
        { id: subjectId }
    );
}

// ── Markers ───────────────────────────────────────────────────────────────────

const MARKER_FIELD_MAP = {
    marker_id:        'markerId',
    marker_name:      'markerName',
    description:      'description',
    unit:             'unit',
    volatility_class: 'volatilityClass',
    storage_type:     'storageType',
    created_at:       'createdAt',
};

const ALL_MARKER_FIELDS = ['marker_id', 'marker_name', 'description', 'unit', 'volatility_class', 'storage_type', 'created_at'];

export async function fetchMarkerData(markerId = null, fields = ALL_MARKER_FIELDS) {
    const gqlFields = fields.map(f => MARKER_FIELD_MAP[f]).join(' ');
    function mapObj(obj) {
        const result = {};
        for (const f of fields) result[f] = obj[MARKER_FIELD_MAP[f]];
        return result;
    }
    if (markerId === null) {
        const data = await gql(`query { markers { ${gqlFields} } }`);
        return data.markers.map(mapObj);
    } else {
        const data = await gql(
            `query($id: String!) { markers(markerId: $id) { ${gqlFields} } }`,
            { id: markerId }
        );
        return data.markers.length ? mapObj(data.markers[0]) : null;
    }
}

/** Returns marker_id string */
export async function createMarker(input) {
    const data = await gql(
        `mutation($input: MarkerInput!) { createMarker(input: $input) { markerId } }`,
        { input }
    );
    return data.createMarker.markerId;
}

export async function updateMarker(markerId, input) {
    await gql(
        `mutation($id: String!, $input: MarkerInput!) { updateMarker(markerId: $id, input: $input) { markerId } }`,
        { id: markerId, input }
    );
}

export async function deleteMarker(markerId) {
    await gql(
        `mutation($id: String!) { deleteMarker(markerId: $id) }`,
        { id: markerId }
    );
}

// ── Measurements ──────────────────────────────────────────────────────────────

const MEASUREMENT_FIELD_MAP = {
    subject_id:  'subjectId',
    marker_id:   'markerId',
    measured_at: 'measuredAt',
    value:       'value',
    quality:     'quality',
    notes:       'notes',
    created_at:  'createdAt',
};

const ALL_MEASUREMENT_FIELDS = ['subject_id', 'marker_id', 'measured_at', 'value', 'quality', 'notes', 'created_at'];

const MEASUREMENT_GQL_FIELDS = ALL_MEASUREMENT_FIELDS.map(f => MEASUREMENT_FIELD_MAP[f]).join(' ');

function mapMeasurement(obj) {
    const result = {};
    for (const f of ALL_MEASUREMENT_FIELDS) result[f] = obj[MEASUREMENT_FIELD_MAP[f]];
    return result;
}

export async function fetchMeasurementsBySubject(subject_id) {
    const data = await gql(
        `query($id: String!) { measurementsBySubject(subjectId: $id) { ${MEASUREMENT_GQL_FIELDS} } }`,
        { id: subject_id }
    );
    return data.measurementsBySubject.map(mapMeasurement);
}

export async function addMeasurement({ subject_id, marker_id, measured_at, value, quality, notes }) {
    const data = await gql(
        `mutation($subjectId: String!, $markerId: String!, $measuredAt: String!, $value: String!, $quality: String, $notes: String) {
            addMeasurement(subjectId: $subjectId, markerId: $markerId, measuredAt: $measuredAt, value: $value, quality: $quality, notes: $notes) {
                ${MEASUREMENT_GQL_FIELDS}
            }
        }`,
        { subjectId: subject_id, markerId: marker_id, measuredAt: measured_at, value, quality, notes }
    );
    return mapMeasurement(data.addMeasurement);
}

export async function deleteMeasurement(subject_id, marker_id, measured_at) {
    await gql(
        `mutation($subjectId: String!, $markerId: String!, $measuredAt: String!) {
            deleteMeasurement(subjectId: $subjectId, markerId: $markerId, measuredAt: $measuredAt)
        }`,
        { subjectId: subject_id, markerId: marker_id, measuredAt: measured_at }
    );
}

// ── Analysis ──────────────────────────────────────────────────────────────────

export async function normalizeHealthScores(measurements, healthy_min, healthy_max) {
    const measurementsInput = measurements.map(m => ({
        markerId: m.marker_id,
        measuredAt: m.measured_at,
        value: m.value,
    }));
    const data = await gql(
        `query($measurements: [RawMeasurementInput!]!, $healthyMin: Float!, $healthyMax: Float!) {
            normalizeHealthScores(measurements: $measurements, healthyMin: $healthyMin, healthyMax: $healthyMax) {
                markerId measuredAt value hScore
            }
        }`,
        { measurements: measurementsInput, healthyMin: healthy_min, healthyMax: healthy_max }
    );
    return data.normalizeHealthScores.map(r => ({
        marker_id: r.markerId,
        measured_at: r.measuredAt,
        value: r.value,
        h_score: r.hScore,
    }));
}
