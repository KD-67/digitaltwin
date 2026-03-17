// Shared GraphQL query constants and typed fetch wrappers.
// All fetch functions return snake_case objects; camelCase normalisation happens here.
// Components import these instead of embedding query strings inline.

import { gql, gqlUpload } from "./gql.js";


// ── Read functions ────────────────────────────────────────────────────────────

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