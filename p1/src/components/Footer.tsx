import Link from 'next/link'
import Image from 'next/image'

export function Footer() {
  return (
    <footer className="border-t border-gray-800 bg-gray-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/logo.png"
                alt="plentyofmoney.online"
                width={36}
                height={36}
                className="rounded-lg"
              />
              <span className="text-lg font-bold text-white">
                plentyofmoney.online
              </span>
            </Link>
            <p className="text-sm text-gray-500">
              Empowering traders with professional-grade signals, education, and tools since 2024.
            </p>
          </div>

          {/* Platform */}
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Platform</h3>
            <ul className="space-y-2">
              <li><Link href="/signals" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">Stock Signals</Link></li>
              <li><Link href="/learn" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">Educational Content</Link></li>
              <li><Link href="/trading" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">Simulated Trading</Link></li>
              <li><Link href="/pricing" className="text-sm text-gray-500 hover:text-gray-300 transition-colors">Pricing</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Company</h3>
            <ul className="space-y-2">
              <li><span className="text-sm text-gray-500">About</span></li>
              <li><span className="text-sm text-gray-500">Careers</span></li>
              <li><span className="text-sm text-gray-500">Blog</span></li>
              <li><span className="text-sm text-gray-500">Contact</span></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-4">Legal</h3>
            <ul className="space-y-2">
              <li><span className="text-sm text-gray-500">Privacy Policy</span></li>
              <li><span className="text-sm text-gray-500">Terms of Service</span></li>
              <li><span className="text-sm text-gray-500">Risk Disclaimer</span></li>
              <li><span className="text-sm text-gray-500">Cookie Policy</span></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800">
          <p className="text-xs text-gray-600 text-center">
            &copy; {new Date().getFullYear()} plentyofmoney.online. All rights reserved. | 
            Trading involves substantial risk of loss. Past performance is not indicative of future results.
          </p>
        </div>
      </div>
    </footer>
  )
}
