from openbatlib import controller

c = controller.Controller()

# Use this method to start the simulation
c.sim(system="I", ref_case="1", dt=1)

a = c.model.E

b = c.model.Ppv.max()

c.print_E()
