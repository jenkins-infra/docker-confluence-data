package org.apache.catalina.realm;

import java.io.IOException;
import java.security.Principal;
import java.util.List;

import javax.naming.NamingException;
import javax.naming.directory.DirContext;

import org.apache.catalina.Context;
import org.apache.catalina.Realm;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.deploy.SecurityConstraint;

public class LdapJdbcRealm extends JNDIRealm implements Realm
{
    private JDBCRealm jdbcRealm = new JDBCRealm();

    protected static final String info = "org.apache.catalina.realm.LdapJdbcRealm/1.0";
    protected static final String name = "LdapJdbcRealm";

    public String getDbConnectionURL() {
        return jdbcRealm.getConnectionURL();
    }

    public void setDbConnectionURL(String dbConnectionURL) {
        jdbcRealm.setConnectionURL(dbConnectionURL);
    }

    public String getUserTable() {
        return jdbcRealm.getUserTable();
    }

    public void setUserTable(String userTable) {
        jdbcRealm.setUserTable(userTable);
    }

    public String getUserNameCol() {
        return jdbcRealm.getUserNameCol();
    }

    public void setUserNameCol(String userNameCol) {
        jdbcRealm.setUserNameCol(userNameCol);
    }

    public String getUserRoleTable() {
        return jdbcRealm.getUserRoleTable();
    }

    public void setUserRoleTable(String userRoleTable) {
        jdbcRealm.setUserRoleTable(userRoleTable);
    }

    public String getRoleNameCol() {
        return jdbcRealm.getRoleNameCol();
    }

    public void setRoleNameCol(String roleNameCol) {
        jdbcRealm.setRoleNameCol(roleNameCol);
    }
    
    public String getDriverName() {
        return jdbcRealm.getDriverName();
    }

    public void setDriverName(String driverName) {
        jdbcRealm.setDriverName(driverName);
    }

    public String getDbConnectionName() {
        return jdbcRealm.getConnectionName();
    }

    public void setDbConnectionName(String connectionName) {
        jdbcRealm.setConnectionName(connectionName);
    }
    
    public String getDbConnectionPassword() {
        return jdbcRealm.getConnectionPassword();
    }

    public void setDbConnectionPassword(String connectionPassword) {
        jdbcRealm.setConnectionPassword(connectionPassword);
    }
    
    public boolean hasResourcePermission(Request request,
                                         Response response,
                                         SecurityConstraint[]constraints,
                                         Context context) throws IOException
    {
        return jdbcRealm.hasResourcePermission(request, response, constraints, context);
    }

    @Override
    public boolean hasRole(Principal principal, String role) {
        return jdbcRealm.hasRole(principal, role);
    }
    
    @Override    
    public SecurityConstraint[] findSecurityConstraints(Request request, Context context) {
    	return jdbcRealm.findSecurityConstraints(request, context);
    }
    
    @Override    
    public boolean hasUserDataPermission(Request request, Response response, SecurityConstraint[] constraint)
            throws java.io.IOException {
        return jdbcRealm.hasUserDataPermission(request,response,constraint);
    }
   
    @Override
    protected List<String> getRoles(DirContext arg0, User arg1)
    		throws NamingException {
    	return jdbcRealm.getRoles(arg1.username);
    }
    
}
