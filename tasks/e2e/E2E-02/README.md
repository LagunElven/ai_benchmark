# E2E-02

This task models an Angular command flowing through an Axon-style aggregate and
event into a JPA-style projection without framework dependencies. The public check
covers one reservation; hidden checks cover sequential events, version guards,
validation and immutability. Only `jpa_projection.py` is relevant to the patch.
