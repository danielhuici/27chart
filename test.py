#include "vr9.dtsi"

#include <dt-bindings/input/input.h>
#include <dt-bindings/mips/lantiq_rcu_gphy.h>

/ {
	compatible = "arcadyan,vrv9510kwac23", "lantiq,xway", "lantiq,vr9";

	chosen {
		bootargs = "console=ttyLTQ0,115200";
	};

	aliases {
		led-boot = &power_green;
		led-failsafe = &power_green;
		led-running = &power_green;
		led-upgrade = &upgrade_blue;
		
		led-dsl = &dsl_green;
		led-internet = &internet_green;
		led-wifi = &wireless_green;
	};

	memory@0 {
		device_type = "memory";
		reg = <0x0 0x10000000>;
	};

	keys {
		compatible = "gpio-keys-polled";
		poll-interval = <100>;

		reset {
			label = "reset";
			gpios = <&gpio 39 GPIO_ACTIVE_LOW>;
			linux,code = <KEY_RESTART>;
		};

		rfkill {
			label = "rfkill";
			gpios = <&gpio 1 GPIO_ACTIVE_LOW>;
			linux,code = <KEY_RFKILL>;
		};
	};

	leds {
		compatible = "gpio-leds";
		
		power_green: power {
			label = "green:power";
			gpios = <&gpio 38 GPIO_ACTIVE_LOW>;
			default-state = "keep";
		};
		internet_red {
			label = "red:internet";
			gpios = <&gpio 27 GPIO_ACTIVE_LOW>;
		};
		internet_green: internet_green {
			label = "green:internet";
			gpios = <&gpio 28 GPIO_ACTIVE_LOW>;
		};
		phone {
			label = "green:phone";
			gpios = <&gpio 43 GPIO_ACTIVE_LOW>;
		};
		dsl_green: dsl_green {
			label = "green:dsl";
			gpios = <&gpio 39 GPIO_ACTIVE_LOW>;
		};
		upgrade_blue : upgrade_blue {
			label = "blue:upgrade";
			gpios = <&gpio 41 GPIO_ACTIVE_LOW>;
		};
		wireless_blue {
			label = "blue:wlan";
			gpios = <&stp 40 GPIO_ACTIVE_LOW>;
		};
		wireless_green: wireless_green {
			label = "green:wlan";
			gpios = <&stp 42 GPIO_ACTIVE_LOW>;
		};
		
	};

	usb_vbus: regulator-usb-vbus {
		compatible = "regulator-fixed";

		regulator-name = "USB_VBUS";

		regulator-min-microvolt = <5000000>;
		regulator-max-microvolt = <5000000>;

		gpio = <&gpio 33 GPIO_ACTIVE_HIGH>;
		enable-active-high;
	};
};

&eth0 {
	pinctrl-0 = <&mdio_pins>,
		    <&gphy0_led1_pins>, <&gphy0_led2_pins>,
		    <&gphy1_led1_pins>, <&gphy1_led2_pins>;
	pinctrl-names = "default";

	interface@0 {
		compatible = "lantiq,xrx200-pdi";
		#address-cells = <1>;
		#size-cells = <0>;
		reg = <0>;
		mac-address = [ 00 11 22 33 44 55 ];
		lantiq,switch;

		ethernet@0 {
			compatible = "lantiq,xrx200-pdi-port";
			reg = <0>;
			phy-mode = "rgmii";
			phy-handle = <&phy0>;
		};
		ethernet@1 {
			compatible = "lantiq,xrx200-pdi-port";
			reg = <1>;
			phy-mode = "rgmii";
			phy-handle = <&phy1>;
		};
		ethernet@2 {
			compatible = "lantiq,xrx200-pdi-port";
			reg = <2>;
			phy-mode = "gmii";
			phy-handle = <&phy11>;
		};
		ethernet@4 {
			compatible = "lantiq,xrx200-pdi-port";
			reg = <4>;
			phy-mode = "gmii";
			phy-handle = <&phy13>;
		};
		ethernet@5 {
			compatible = "lantiq,xrx200-pdi-port";
			reg = <5>;
			phy-mode = "rgmii";
			phy-handle = <&phy5>;
		};
	};

	mdio {
		#address-cells = <1>;
		#size-cells = <0>;
		compatible = "lantiq,xrx200-mdio";

		phy0: ethernet-phy@0 {
			reg = <0x0>;
			compatible = "lantiq,phy11g", "ethernet-phy-ieee802.3-c22";
		};
		phy1: ethernet-phy@1 {
			reg = <0x1>;
			compatible = "lantiq,phy11g", "ethernet-phy-ieee802.3-c22";
		};
		phy5: ethernet-phy@5 {
			reg = <0x5>;
			compatible = "lantiq,phy11g", "ethernet-phy-ieee802.3-c22";
		};
		phy11: ethernet-phy@11 {
			reg = <0x11>;
			compatible = "lantiq,phy11g", "ethernet-phy-ieee802.3-c22";
		};
		phy13: ethernet-phy@13 {
			reg = <0x13>;
			compatible = "lantiq,phy11g", "ethernet-phy-ieee802.3-c22";
		};
	};
};

&gphy0 {
	lantiq,gphy-mode = <GPHY_MODE_GE>;
};

&gphy1 {
	lantiq,gphy-mode = <GPHY_MODE_GE>;
};

&gpio {
	pinctrl-names = "default";
	pinctrl-0 = <&state_default>;

	state_default: pinmux {
		exin3 {
			lantiq,groups = "exin3";
			lantiq,function = "exin";
		};
		pci_rst {
			lantiq,pins = "io21";
			lantiq,output = <1>;
			lantiq,open-drain = <0>;
			lantiq,pull = <2>;
		};
		pcie-rst {
			lantiq,pins = "io38";
			lantiq,pull = <0>;
			lantiq,output = <1>;
		};
		ifxhcd-rst {
			lantiq,pins = "io33";
			lantiq,pull = <0>;
			lantiq,open-drain = <0>;
			lantiq,output = <1>;
		};
	};
};

&localbus {
	flash@0 {
		compatible = "lantiq,nand-xway";
		lantiq,cs = <1>;
		bank-width = <2>;
		reg = <0 0x0 0x2000000>;

		pinctrl-0 = <&nand_pins>, <&nand_cs1_pins>;
		pinctrl-names = "default";

		partitions {
			compatible = "fixed-partitions";
			#address-cells = <1>;
			#size-cells = <1>;

			partition@0 {
				label = "uboot";
				reg = <0x00000 0x40000>;
			};
			partition@40000 {
				label = "u-boot-env";
				reg = <0x40000 0x20000>;
			};
			partition@60000 {
				label = "kernel";
				reg = <0x60000 0x300000>;
			};
			partition@360000 {
				label = "ubi";
				reg = <0x360000 0x7ca0000>;
			};
		};
	};
};

&pci0 {
	status = "okay";

	pinctrl-0 = <&pci_gnt1_pins>, <&pci_req1_pins>;
	pinctrl-names = "default";

	gpio-reset = <&gpio 21 GPIO_ACTIVE_HIGH>;
};

&stp {
	status = "okay";
};

&usb_phy0 {
	status = "okay";
};

&usb_phy1 {
	status = "okay";
};

&usb0 {
	status = "okay";
	vbus-supply = <&usb_vbus>;
};

&usb1 {
	status = "okay";
	vbus-supply = <&usb_vbus>;
};


&pci0 {
	wifi@1814,3062 {
		compatible = "pci1814,3062";
		reg = <0x7000 0 0 0 0>;
		ralink,eeprom = "RT3062.eeprom";
	};
};


&pcie0 {
	status = "disabled";
};