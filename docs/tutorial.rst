********************************************************************************
Tutorial
********************************************************************************

More info coming soon ...


.. code-block:: python

    from compas.datastructures import Mesh
    from compas_session.namedsession import NamedSession

    session = NamedSession("COMPAS")
    scene = session.scene()

    mesh = Mesh.from_meshgrid(10, 10)
    scene.add(mesh)
    scene.record("Add Mesh")

    session.dump("session.json")
