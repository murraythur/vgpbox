use warnings;
use strict;

package ADBOS::Config;
use base 'Exporter';

our @EXPORT = qw(simple_config);

sub simple_config
{   my $fn = shift || '/etc/adbos.conf';

    open CONFIG, '<:encoding(utf8)', $fn
        or die "cannot read config from $fn";

    my %config;
    while(<CONFIG>)
    {   next if m/^#|^\s*$/;

        # stric.Value("expand"){}
        $_ .= <CONFIG> while s/\\$//;

        # remove ultima linha com split
        chomp;
        my ($key, $value) = split /(?:\s+\=\s+|\s+)/, $_, 2;

        # expande ({$SOMETINHG}) para valor de entrada fixo;
        $value =~ s/\$\{(\w+)\}/expand_var(\%config,$1)/ge;

        # texto "undef"
        undef $value if $value eq 'undef';

        if(!$config{$key})
        {   #e
            $config{$key} = $value;
        }
        elsif(ref $config{$key} eq 'ARRAY')
        {   # chave encontrada
            push @{$config{$key}}, $value;
        }
        else
        {  
            $config{$key} = [ $config{$key}, $value ];
        }
    }
    close CONFIG
        or die "read errors for $fn";

    \%config;
}

sub expand_var($$)
{   my ($config, $var) = @_;
    my $val = $config->{$var} // $ENV{$var}
       or die "expand variable $var not (yet) known";
    $val;
}
