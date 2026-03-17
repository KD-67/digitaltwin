// Shared GraphQL client utility.
// Provides gql() for queries/mutations

const GQL_URL    = "http://localhost:8000/graphql";

/** Send a query or mutation. Returns data or throws with the first GraphQL error message. */
export async function gql(query, variables = {}) {
    const res  = await fetch(GQL_URL, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ query, variables }),
    });
    const json = await res.json();
    if (json.errors?.length) throw new Error(json.errors[0].message);
    return json.data;
}