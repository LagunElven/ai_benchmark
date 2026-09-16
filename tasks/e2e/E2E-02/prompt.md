# E2E-02 - Angular command to Axon event to JPA projection

The dependency-free adapters in this workspace represent one cross-layer stock
reservation: `angular_client.py` builds the wire command, `axon_aggregate.py`
emits a `StockReserved` event, `jpa_projection.py` updates the read model, and
`workflow.py` composes the path.

Fix only `jpa_projection.py`. Applying a valid event must return a new read model,
preserve its product id, set `available` from the event remaining quantity, add the
event quantity to the existing `reserved` amount, and advance the read-model
version by exactly one. Reject a wrong event type, another aggregate, invalid
quantity/remaining values or a skipped/repeated version with `ValueError`. Do not
change the Angular, Axon, workflow or test files. Return only the
`file_changes_v1` JSON object.
