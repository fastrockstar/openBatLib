<table>

<tr>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/fastrockstar/openBatLib/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/fastrockstar/openBatLib" alt="license" />
    </a>
</td>
</tr>
  <td>Build Status</td>
  <td>
    <a href='https://openbatlib.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/openbatlib/badge/?version=latest' alt='Documentation Status' />
    </a>
  </td>
</tr>
</table>

openBatLib is a tool that provides a set of 
functions and classes for simulating the performance of photovoltaic
energy storing systems. openBatLib was originally ported from the PerMod MATLAB
toolbox developed at HTW Berlin and it implements many
of the models and methods developed at the Labs. More information on
PerMod can be found at https://pvspeicher.htw-berlin.de/permod/.

Getting Started
=============
The following section describes the quickest way to calculate a simulation using openBatLib.
The first step is to create an instance of the `Controller` class.
```python 
c = controller.Controller()
```
This class allows simulations in different ways. For this short tutotiral we use the `sim()` method. Using this method, the first step is to select the model to be simulated. An Excel file for this is available under `parameter`, in which all currently supported systems are listed. Other parameters required for the simulation are PV generator and load values. openBatLib offers two different reference cases containing those values to choose from.
For this example we use the __system__ `H`(an AC-coupled battery system) and the __reference case__ ` 1`. System `H` represents . This reference case represents a household with annual needs of 5010 kWh and a nominal PV power of 5 kWp.
```python
c.sim(system="I", ref_case="1")
```
The method `print_E` gives an overview of the energies of the simulation.
```
Name       MWh       
El         5.0233    
Epv        5.2219    
Ebatin     1.8925    
Ebatout    1.8332    
Eac2g      1.568     
Eg2ac      1.9404    
Eg2l       1.8788    
Eperi      0.0133    
Ect        0.0396    
Epvs       5.0319    
Eac2bs     2.0568    
Ebs2ac     1.6758    
Epvs2l     1.5024    
Epvs2bs    1.9952    
Eg2bs      0.0616    
Epvs2g     1.5342    
Ebs2l      1.6421    
Ebs2g      0.0338    
```

Documentation
=============

A full documentation can be found at [readthedocs](https://openbatlib.readthedocs.io/). 


Contributing
============

We need your help to make openBatLib a great tool!

The long-term success of openBatLib requires substantial community support.


License
=======

MIT
