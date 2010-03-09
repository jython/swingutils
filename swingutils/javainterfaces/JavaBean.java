package swingutils.javainterfaces;

import java.beans.PropertyChangeListener;

public interface JavaBean {
     void addPropertyChangeListener(PropertyChangeListener listener);

     void addPropertyChangeListener(String name, PropertyChangeListener pcl);
     
     void removePropertyChangeListener(PropertyChangeListener listener);

     void removePropertyChangeListener(String name, PropertyChangeListener pcl);
}