### RPM external openssl 0.9.8e
Source: http://cmsrep.cern.ch/cmssw/openssl-sources/%n-fips-%realversion-usa.tar.bz2
Patch0: openssl-0.9.8e-rh-0.9.8e-12.el5_4.6

%prep
%setup -n %n-fips-%{realversion}
%patch0 -p1

%build
# Looks like rpmbuild passes its own sets of flags via the
# RPM_OPT_FLAGS environment variable and those flags include
# -m64 (probably since rpmbuild processor detection is not
# fooled by linux32). A quick fix is to just set the variable
# to "" but we should probably understand how rpm determines
# those flags and use them for our own good.
export RPM_OPT_FLAGS="-O2 -g -pipe -Wall -Wp,-DOPENSSL_USE_NEW_FUNCTIONS -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -mtune=generic"

case %cmsplatf in
  osx*)
    perl -p -i -e 's|-compatibility_version.*|-compatibility_version \${SHLIB_MAJOR}.\${SHLIB_MINOR} \\|' Makefile.ssl ;;
esac

./config --prefix=%i enable-seed enable-tlsext enable-rfc3779 \
                     no-idea no-mdc2 no-rc5 no-ec no-ecdh no-ecdsa shared

make
%install
make install
rm -rf %{i}/lib/pkgconfig

# MacOSX is case insensitive and the man page structure has case sensitive logic
case %cmsplatf in
    osx* ) 
        rm -rf %{i}/ssl/man
    ;;
esac
perl -p -i -e "s|^#!.*perl|#!/usr/bin/env perl|" %{i}/ssl/misc/CA.pl %{i}/ssl/misc/der_chop %{i}/bin/c_rehash
#
# SCRAM ToolBox toolfile
mkdir -p %i/etc/scram.d
cat << \EOF_TOOLFILE >%i/etc/scram.d/%n
<doc type=BuildSystem::ToolDoc version=1.0>
<Tool name=%n version=%v>
<lib name=ssl>
<lib name=crypto>
<client>
 <Environment name=OPENSSL_BASE default="%i"></Environment>
 <Environment name=INCLUDE default="$OPENSSL_BASE/include"></Environment>
 <Environment name=LIBDIR  default="$OPENSSL_BASE/lib"></Environment>
</client>
</Tool>
EOF_TOOLFILE

%post
%{relocateConfig}etc/scram.d/%n
