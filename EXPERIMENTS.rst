***********
Experiments
***********

The test cases are stored in ``experiment_data/`` directory.
Here is the schema:
``experiment_data/{experiment}/{expected or unexpected}/{case name}/model.json``.

The outputs are recorded in ``experiment_output``, follwing the schema:
``experiment_output/{experiment}/{LLM}/{relative path to case directory}``,
where each output contains the concrete prompt, ``prompt.txt``, and the corresponding ``response.txt``.
