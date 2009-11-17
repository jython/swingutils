from swingutils.binding import PropertyAdapter


class CalendarAdapter(PropertyAdapter):
    def __init__(self, holder, srcProperty, dateChooser):
        PropertyAdapter.__init__(self, holder, srcProperty, dateChooser,
                                 u'date')
    
    def propertyChange(self, event):
        PropertyAdapter.propertyChange(self, event)
        self.destination.enabled = self.source.value is not None


def bindDateChooser(holder, srcProperty, dateChooser, twoway=True):
    adapter = CalendarAdapter(holder, srcProperty, dateChooser)
    holder.addPropertyChangeListener(srcProperty, adapter)
    if twoway:
        dateChooser.addPropertyChangeListener(u'date', adapter)
